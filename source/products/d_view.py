import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import dining_common as C
args = json.loads(sys.argv[sys.argv.index('--') + 1])
key = args.pop('key'); out = args.pop('out')
C.render_preview(key, out=out, **args)
