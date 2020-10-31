import sys
import csv
import re
from bs4 import BeautifulSoup


def main(args):
    if len(args) < 3:
        print(f'Usage: {args[0]} InputHTMLFilePath OutputCsvPath')
        exit(1)

    input_file_path = args[1]
    output_file_path = args[2]

    with open(output_file_path, 'w', encoding='shift_jis', newline='') as csv_output, \
            open(input_file_path, 'r', encoding='utf-8', newline='') as html_input:
        soup = BeautifulSoup(html_input, 'html.parser')
        orders_soup = soup.find('div', {'class': 'manage-sales-orders'})

        output_list = list()

        for order_soup in orders_soup.children:
            order_no = ''
            order_date = ''
            income_amount = 0
            outgo_records = dict()
            for row in order_soup.find_all('div', {'class': 'co-breakdown-table-row'}):
                name: str = row.contents[0].get_text()
                value: str = row.contents[1].get_text()
                negative: bool = 'co-breakdown-table-value-negative' in row.contents[1].get('class')

                if name.startswith('注文番号'):
                    order_no = value
                elif name.startswith('注文日時'):
                    order_date = value
                else:
                    v = int(value.translate(str.maketrans('', '', ', ¥')))
                    if negative:
                        outgo_records[name] = v
                    else:
                        income_amount += v

            order_date = re.match(r'(\d*)年(\d*)月(\d*)日 \d*時\d*分', order_date).expand(r'\1-\2-\3')

            output_list.append(['収入', order_date, '売上高', income_amount, 'BOOTH', 'BOOTH', order_no])
            for name, outgo in outgo_records.items():
                output_list.append(
                    ['', order_date, '支払手数料' if name.startswith('手数料') else '荷造運賃', -outgo, 'BOOTH', '', ''])

        csv_writer = csv.writer(csv_output)
        csv_writer.writerows(output_list)


if __name__ == '__main__':
    main(sys.argv)
