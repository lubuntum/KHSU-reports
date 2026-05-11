import json
from io import BytesIO

import pandas as pd
from collections import defaultdict
from pathlib import Path
def calculate_lessons_hours(data, teacher, month):
    # Dictionary to store counts
    lesson_counts = defaultdict(int)
    # Extract lessons from all weeks
    for week in data:
        if 'days' in week:
            for day in week['days']:
                if 'lessons' in day and day['lessons'] is not None:
                    for lesson in day['lessons']:
                        if lesson is not None:
                            subject = lesson.get('subject', '')
                            groups = lesson.get('group', [])
                            type_lesson = lesson.get('type_lesson', '')

                            # Handle multiple groups
                            for group in groups:
                                key = (subject, group, type_lesson)
                                lesson_counts[key] += 1
                                print(f"DEBUG: Added lesson: {key}")
    # Prepare data for DataFrame
    rows = []
    for (subject, group, type_lesson), count in lesson_counts.items():
        academic_hours = count * 2
        rows.append({
            'Subject': subject,
            'Group': group,
            'Type of Lesson': type_lesson,
            'Count': count,
            'Academic Hours (Count * 2)': academic_hours
        })

    # Create DataFrame
    df = pd.DataFrame(rows)
    # Sort by Subject, then Group, then Type of Lesson
    if not df.empty:
        df = df.sort_values(['Subject', 'Group', 'Type of Lesson']).reset_index(drop=True)
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Lessons Summary', index=False)

        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Lessons Summary']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2C3E50',
            'font_color': 'white',
            'border': 1
        })

        # Write headers with formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Adjust column widths
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(column_width, 50))
    output.seek(0)
    print(f"DEBUG: BytesIO size after seek: {output.getbuffer().nbytes} bytes")
    if output.getbuffer().nbytes == 0:
        return None
    return output