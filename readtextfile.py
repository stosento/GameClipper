import re

reg_string = '(0?[1-9]|1[0-9]):[0-5][0-9]|0:[0-5][0-9]|:[0-5][0-9]|[0-5][0-9]\.[0-9]$|[0-9]{4}|[0-9]{3}|[0-9].[0-5][0-9]'
reg_pattern = re.compile(reg_string)

ts_string = '[0-9]:[0-5][0-9]:[0-5][0-9]'
ts_pattern = re.compile(ts_string)

def read_file(txt_file, starttime):
    times = []
    checkstart = False
    paststart = True

    if starttime:
        checkstart = True
        paststart = False

    with open(txt_file, 'r') as f:
        for line in f:
            m = re.search(reg_pattern, line)
            if m:
                m_string = m.group()
            if checkstart:
                if m_string == starttime:
                    checkstart = False
                    paststart = True
            if paststart:
                times.append(m_string)

    print("timestamps:", times)
    return times

def read_ts_file(txt_file):
    times = []

    with open(txt_file, 'r') as f:
        for line in f:
            m = re.search(ts_pattern, line)
            if m:
                times.append(m.group())

    print("timestamps:", times)
    return times

