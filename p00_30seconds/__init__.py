
def run(dry_run: bool = False):
    """
    run all submodules
    """
    from pkgutil import iter_modules
    from pathlib import Path
    from importlib import import_module
    exec_status = {}
    for (_, name, _) in iter_modules([Path(__file__).parent]):
        try:
            import_module('.' + name, package=__name__).main(dry_run)
        except Exception as err:
            exec_status[name] = "Exception: " + str(err)
            continue
        exec_status[name] = "Ok"
    return exec_status
