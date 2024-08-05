# agents names
INITIALIZER = 'initializer'
EXECUTOR = 'executor'
PENTEST = 'pentest'
TEAM_LEAD = 'team_lead'
TASK_SUPERVISOR = 'task_supervisor'

# path to msf modules names
REPLACEMENT_PRELIMINARY_MODULES = 'msf_modules/preliminary_modules.txt'
REPLACEMENT_AUXILIARY_MODULES = 'msf_modules/auxiliary_modules.txt'

# placeholders
TEXT_INSIDE_BRACES_PATTERN = r'\{(.*?)\}'

# others
PREFIX_REPLACEMENT = 'REPLACEMENT_'

# msf_tools.py constant
KEYWORDS = ['execution completed', 'OptionValidateError']
TIMEOUT = 30000000

# some flag
MOCK: bool = True

#database
TABLE_NAME: str|None = None

