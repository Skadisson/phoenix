from bin.service import Logger
from bin.service import Environment
from bin.service import SciKitLearn

logger = Logger.Logger()
environment = Environment.Environment()
try:

    print('--- training started ---')
    scikit = SciKitLearn.SciKitLearn()
    scikit.train()

except Exception as e:
    print(e)
    logger.add_entry('PhoenixSync', e)
