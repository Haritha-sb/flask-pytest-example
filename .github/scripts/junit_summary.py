"""Render a pytest JUnit XML report as a markdown table."""
import sys
import xml.etree.ElementTree as ET

MARKER = '<!-- ci-test-results -->'

RESULTS = {
    'failure': ('Failed', ':x:'),
    'error': ('Error', ':x:'),
    'skipped': ('Skipped', ':heavy_minus_sign:'),
}


def classify(case):
    for tag, (label, icon) in RESULTS.items():
        if case.find(tag) is not None:
            return label, icon
    return 'Passed', ':white_check_mark:'


def render(path):
    root = ET.parse(path).getroot()
    suites = root.iter('testsuite') if root.tag == 'testsuites' else [root]

    rows = []
    counts = {}
    for suite in suites:
        for case in suite.iter('testcase'):
            label, icon = classify(case)
            counts[label] = counts.get(label, 0) + 1
            name = case.get('name', '')
            where = case.get('classname', '').replace('.', '/')
            seconds = float(case.get('time', 0) or 0)
            rows.append('| %s %s | `%s` | `%s` | %.2fs |' % (icon, label, name, where, seconds))

    total = len(rows)
    tally = ', '.join('%d %s' % (n, label.lower()) for label, n in sorted(counts.items()))

    lines = [
        MARKER,
        '## Test results',
        '',
        '**%d test%s** - %s' % (total, '' if total == 1 else 's', tally or 'no results'),
        '',
        '| Result | Test | Location | Time |',
        '| --- | --- | --- | --- |',
    ]
    lines.extend(rows)
    return '\n'.join(lines)


if __name__ == '__main__':
    print(render(sys.argv[1]))
