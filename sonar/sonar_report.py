import openpyxl, requests, json
from enum import Enum
from operator import itemgetter
from itertools import groupby
from base_tool.excel_tool import *
from datetime import datetime


class Metric(Enum):
    BUG = 'bugs'
    VULNERABILITY = 'vulnerabilities'
    CODE_SMELL = 'code_smells'
    SQALE_INDEX = 'sqale_index'
    DUPLICATED_LINES_DENSITY = 'duplicated_lines_density'
    DUPLICATED_LINES = 'duplicated_lines'
    COVERAGE = 'coverage'
    LINES = 'ncloc'


class ModuleSonarInfo:
    def __init__(self):
        self.module = ''
        self.bug_count = 0
        self.vulnerabilities_count = 0
        self.code_smell_count = 0
        self.duplicate_lines = 0
        self.duplicate_rate = 0
        self.sqale_index = 0
        self.code_smell_rate = 0
        self.lines = 0


module_name_list = ['com.kaifa.cloud:archive-service',
                    'com.kaifa.cloud:big-data-service',
                    'com.kaifa.cloud:gas-service',
                    'com.kaifa.cloud:hes-service',
                    'com.kaifa.cloud:ivy-app-service',
                    'com.kaifa.cloud:ivy-service',
                    'com.kaifa.cloud:job-service',
                    'com.kaifa.cloud:juniper-service',
                    'com.kaifa.cloud:mdm-service',
                    'com.kaifa.cloud:prepay-service',
                    'com.kaifa.cloud:smart-app-service',
                    'com.kaifa.cloud:system-service',
                    'com.kaifa.cloud:test-service',
                    'com.kaifa.cloud:water-service']

metric_list = []
for metric in Metric:
    metric_list.append(metric.value)

measure_url = 'http://10.32.233.210:9000/api/measures/search'

result = requests.get(measure_url, {
    'projectKeys': ','.join(module_name_list),
    'metricKeys': ','.join(metric_list)
})

data_list = json.loads(result.content).get('measures')
data_list.sort(key=itemgetter('component'))
data_group = groupby(data_list, itemgetter('component'))
module_list = []
for key, group in data_group:
    module = ModuleSonarInfo()
    module.module = key.split(':')[1]
    data_map = {}
    for data in group:
        data_map[data.get('metric')] = data
    module.bug_count = int(data_map.get(Metric.BUG.value).get('value'))
    module.code_smell_count = int(data_map.get(Metric.CODE_SMELL.value).get('value'))
    module.duplicate_lines = int(data_map.get(Metric.DUPLICATED_LINES.value).get('value'))
    module.duplicate_rate = round(float(data_map.get(Metric.DUPLICATED_LINES_DENSITY.value).get('value')) / 100, 4)
    module.vulnerabilities_count = int(data_map.get(Metric.VULNERABILITY.value).get('value'))
    module.lines = int(data_map.get(Metric.LINES.value).get('value'))
    module.sqale_index = int(int(data_map.get(Metric.SQALE_INDEX.value).get('value')) / 480)
    module.code_smell_rate = round((float(module.code_smell_count) / module.lines), 4)
    module_list.append(module)

workbook = openpyxl.load_workbook('template/Java Web Sonar Report Template.xlsx')

sheet = workbook.get_active_sheet()

set_sheet_data(sheet, module_list)

workbook.save("Java Web Sonar Report-" + datetime.today().strftime('%Y%m%d') + '.xlsx')
