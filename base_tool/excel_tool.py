from copy import copy

class ExcelData:
    pass


class ExcelStyle:
    def __init__(self, font=None, border=None, alignment=None, fill=None,number_format='@'):
        self.font = font
        self.fill = fill
        self.alignment = alignment
        self.border = border
        self.number_format=number_format


def set_row_font(worksheet, row, num, style):
    for i in range(1, num + 1):
        worksheet.cell(row, i).font = style


def set_row_border(worksheet, row, num, style):
    for i in range(1, num + 1):
        worksheet.cell(row, i).border = style


def set_row_align(worksheet, row, num, style):
    for i in range(1, num + 1):
        worksheet.cell(row, i).alignment = style


def get_attr_list(worksheet, num=None,clear_comment=False):
    attr_list = []
    flag = False
    if num == None:
        num = 99
        flag = True
    for i in range(1, num + 1):
        cell = worksheet.cell(1, i)
        text = cell.comment.text.strip('''\n''')
        if clear_comment:
            cell.comment.text = ''
        if flag:
            if text.endswith(';'):
                text = text.rstrip(';')
                attr_list.append(text)
                break
            else:
                attr_list.append(text)
    return attr_list


def set_sheet_data(worksheet, data_list, style=None, attr_list=None, num=None):
    if style is None:
        style = get_template_style(worksheet)
    if attr_list is None:
        attr_list = get_attr_list(worksheet, num,clear_comment=True)
    for i in range(len(data_list)):
        print(i)
        for j in range(len(attr_list)):
            cell = worksheet.cell(i + 2, j + 1)
            if attr_list[j] == 'no':
                cell.value = i + 1
            else:
                value = getattr(data_list[i], attr_list[j])
                if value is not None:
                    if isinstance(value,str):
                        value = value.strip('=').strip(' ')
                    cell.value = value
            if isinstance(style,list):
                style_data = style[j]
            else:
                style_data = style
            cell.border = style_data.border
            cell.font = style_data.font
            cell.alignment = style_data.alignment
            cell.number_format = style_data.number_format


def get_sheet_data(worksheet, clazz=ExcelData, attr_list=None):
    if attr_list is None:
        attr_list = get_attr_list(worksheet)
    count = 0

    while worksheet.cell(count + 2, 1).value is not None:
        count = count + 1

    result_list = []
    for i in range(0, count):
        ob = clazz()
        for j in range(0, len(attr_list)):
            if attr_list[j] == 'no':
                continue
            value = str(worksheet.cell(i + 2, j + 1).value).strip('''\n''')
            setattr(ob, attr_list[j], value)
        result_list.append(ob)
    return result_list

def get_template_style(worksheet=None,workbook=None):
    attr_list = get_attr_list(worksheet)
    style_list = []
    if workbook is not None:
        worksheet = workbook.active
    for j in range(len(attr_list)):
        cell = worksheet.cell(2, j + 1)
        border = cell.border
        font = cell.font
        alignment = cell.alignment
        fill = cell.fill
        number_format = cell.number_format
        style_list.append(ExcelStyle(copy(font),copy(border), copy(alignment),copy(fill),copy(number_format)))
    return style_list
