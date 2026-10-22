"""Preview tweak for wall items (does not modify plib): Standard view transform, slight negative exposure."""
import plib
_orig = plib.setup_render
def _sr(*a, **k):
    s = _orig(*a, **k)
    try:
        s.view_settings.view_transform = 'Standard'
        s.view_settings.exposure = -1.5
    except Exception:
        pass
    return s
plib.setup_render = _sr
