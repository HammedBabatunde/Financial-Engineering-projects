import pdfplumber
import re
import csv
import sys
import os

def convert_pdf_to_csv(pdf_path, csv_path):
    # Patterns for identifying core lines (with date and time)
    trans_time_pat = re.compile(r"^\d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2}$")
    value_date_pat = re.compile(r"^\d{1,2} [A-Za-z]{3} \d{4}$")

    # Column ranges for Wallet Account (pages 1-92, and top of page 93)
    wallet_cols = [
        ('col0', 0, 125),
        ('col1', 125, 170),
        ('col2', 170, 300),
        ('col3', 300, 335),
        ('col4', 335, 375),
        ('col5', 375, 415),
        ('col6', 415, 460),
        ('col7', 460, 1000)
    ]

    # Column ranges for Savings Account (bottom of page 93, and pages 94-139)
    savings_cols = [
        ('col0', 0, 135),
        ('col1', 135, 180),
        ('col2', 180, 245),
        ('col3', 245, 290),
        ('col4', 290, 335),
        ('col5', 335, 385),
        ('col6', 385, 435),
        ('col7', 435, 1000)
    ]

    pdf = pdfplumber.open(pdf_path)
    print(f"Opened {pdf_path} with {len(pdf.pages)} pages.")

    all_page_groups = []

    for page_idx, page in enumerate(pdf.pages):
        words = page.extract_words()
        if not words:
            continue
        
        page_num = page_idx + 1
        
        # Group words by top coordinate within a tolerance of 3.0 points
        lines = {}
        for w in words:
            found = False
            for t in lines:
                if abs(w['top'] - t) < 3:
                    lines[t].append(w)
                    break
            if not found:
                lines[w['top']] = [w]
                
        sorted_tops = sorted(lines.keys())
        page_lines = []
        
        for t in sorted_tops:
            # Layout transitions from Wallet to Savings on Page 93 at t = 440
            if page_num <= 92:
                cols = wallet_cols
            elif page_num == 93:
                cols = wallet_cols if t < 440 else savings_cols
            else:
                cols = savings_cols
                
            line_words = sorted(lines[t], key=lambda x: x['x0'])
            row = {c[0]: [] for c in cols}
            for w in line_words:
                assigned = False
                for name, xmin, xmax in cols:
                    if xmin <= w['x0'] < xmax:
                        row[name].append(w['text'])
                        assigned = True
                        break
                if not assigned:
                    row['col2'].append(w['text'])
                    
            row_data = {k: ' '.join(v).strip() for k, v in row.items()}
            
            # Check if the line itself is metadata and should be filtered out
            text_content = ' '.join(row_data.values()).strip()
            if not text_content:
                continue
                
            is_meta_line = False
            # Rule 1: Page 1 metadata
            if page_num == 1 and t < 350:
                is_meta_line = True
            # Rule 2: Page 93 transition metadata
            elif page_num == 93 and 440 <= t < 570:
                is_meta_line = True
            # Rule 3: Any table headers
            elif 'Trans. Time' in row_data['col0'] or 'Value Date' in row_data['col1']:
                is_meta_line = True
            # Rule 4: Header tails and table titles
            elif text_content in ['₦)', '₦', ')', 'Balance After(']:
                is_meta_line = True
            # Rule 5: Trailing date on the last page
            elif page_num == len(pdf.pages) and re.match(r"^\d{1,2} [A-Za-z]{3} \d{4}$", text_content):
                is_meta_line = True
                
            if is_meta_line:
                continue
                
            page_lines.append({
                'page': page_num,
                'top': t,
                'data': row_data,
                'is_core': bool(trans_time_pat.match(row_data['col0']) and value_date_pat.match(row_data['col1']))
            })
            
        if not page_lines:
            continue
            
        # Group page lines by vertical gap (threshold = 12.0)
        groups = []
        current_group = [page_lines[0]]
        for item in page_lines[1:]:
            t = item['top']
            prev_t = current_group[-1]['top']
            if t - prev_t > 12.0:
                groups.append(current_group)
                current_group = [item]
            else:
                current_group.append(item)
        if current_group:
            groups.append(current_group)
            
        all_page_groups.append((page_num, groups))

    # Filter out groups (our line-level filters already took care of metadata)
    filtered_groups = []
    for page_num, groups in all_page_groups:
        for g in groups:
            filtered_groups.append(g)

    # Stitch groups with 0 core lines (page break splits)
    stitched_groups = []
    for g in filtered_groups:
        cc = sum(1 for line in g if line['is_core'])
        if cc > 0:
            stitched_groups.append(g)
        else:
            if stitched_groups:
                stitched_groups[-1].extend(g)
            else:
                stitched_groups.append(g)

    # If the first group had 0 core lines, merge it into the second group
    if stitched_groups and sum(1 for line in stitched_groups[0] if line['is_core']) == 0:
        if len(stitched_groups) > 1:
            first = stitched_groups.pop(0)
            stitched_groups[0] = first + stitched_groups[0]

    # Extract transaction fields from each group
    transactions = []
    for g_idx, g in enumerate(stitched_groups):
        core_line = None
        for line in g:
            if line['is_core']:
                core_line = line
                break
                
        if not core_line:
            print(f"WARNING: Group {g_idx} has no core line!")
            continue
            
        # Reconstruct Description and Reference
        sorted_lines = sorted(g, key=lambda x: (x['page'], x['top']))
        
        desc_parts = []
        ref_parts = []
        
        for line in sorted_lines:
            data = line['data']
            if data['col2']:
                desc_parts.append(data['col2'])
            if data['col7']:
                ref_parts.append(data['col7'])
                
        description = " ".join(desc_parts).strip()
        clean_ref_parts = [r.replace(" ", "") for r in ref_parts]
        transaction_ref = "".join(clean_ref_parts).strip()
        
        # Rest of the fields from core line
        trans_date = core_line['data']['col0']
        val_date = core_line['data']['col1']
        debit = core_line['data']['col3']
        credit = core_line['data']['col4']
        balance = core_line['data']['col5']
        channel = core_line['data']['col6']
        
        # Save the transaction
        transactions.append({
            'Trans. Date': trans_date,
            'Value Date': val_date,
            'Description': description,
            'Debit(₦)': debit,
            'Credit(₦)': credit,
            'Balance After(₦)': balance,
            'Channel': channel,
            'Transaction Reference': transaction_ref
        })

    # Write to CSV
    headers = ['Trans. Date', 'Value Date', 'Description', 'Debit(₦)', 'Credit(₦)', 'Balance After(₦)', 'Channel', 'Transaction Reference']
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(transactions)

    print(f"Successfully wrote {len(transactions)} rows to {csv_path}")
    return len(transactions)

if __name__ == "__main__":
    pdf = "/Users/user/Desktop/Python-for-Financial-Engineering/savings_engine_project/BABATUNDE IDRIS HAMMED_7051318786_20260615151313.pdf"
    csv_out = "/Users/user/Desktop/Python-for-Financial-Engineering/savings_engine_project/statement.csv"
    convert_pdf_to_csv(pdf, csv_out)
