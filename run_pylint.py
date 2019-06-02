import argparse
import sys
from pylint import lint

desc = "PyLint wrapper that add the --fail-under option."\
       " All other arguments are passed to pylint."
parser = argparse.ArgumentParser(description=desc, allow_abbrev=False)
parser.add_argument('--fail-under', dest='threshold', type=float, default=8,
                    help='If the final score is more than THRESHOLD, exit with'
                    ' exitcode 0, and pylint\'s exitcode otherwise.')

args, remaining_args = parser.parse_known_args()

threshold = args.threshold

run = lint.Run(remaining_args, do_exit=False)
score = run.linter.stats['global_note'] # Yes this is a terrible name for the score

if score < threshold:
    print('Not pass, pylint score less than threshold')
    sys.exit(run.linter.msg_status)

else:
	print('Code passed')
