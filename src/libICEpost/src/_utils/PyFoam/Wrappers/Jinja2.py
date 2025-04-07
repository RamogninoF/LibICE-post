"""Wrapper for the Jinja2-library

Adds PyFoam-specific  filters and tests to the environment"""

__all__ = ["get_jinja_environment"]

try:
    import jinja2
    _has_jinja = True
    _has_pass_context = hasattr(jinja2, "pass_context")

except ImportError:
    _has_jinja = False


_environments = {}


def parse_foam_file(name,
                    boundaryDict=False,
                    listDict=False,
                    listDictWithHeader=False,
                    noHeader=False,
                    noBody=False,
                    binaryMode=False):
    from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

    pf = ParsedParameterFile(name,
                             boundaryDict=boundaryDict,
                             listDict=listDict,
                             listDictWithHeader=listDictWithHeader,
                             noBody=noBody,
                             noHeader=noHeader,
                             binaryMode=binaryMode)

    return pf


def parse_foam_string(content,
                      boundaryDict=False,
                      listDict=False,
                      listDictWithHeader=False,
                      noHeader=True,
                      noBody=False,
                      binaryMode=False):
    from PyFoam.RunDictionary.ParsedParameterFile import FoamFileParser

    pf = FoamFileParser(content,
                        boundaryDict=boundaryDict,
                        listDict=listDict,
                        listDictWithHeader=listDictWithHeader,
                        noBody=noBody,
                        noHeader=noHeader,
                        binaryMode=binaryMode)

    return pf


def format_foam(data):
    from PyFoam.Basics.FoamFileGenerator import makeString

    return makeString(data)


def solution_dir(location):
    from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

    return SolutionDirectory(location)


def import_module(name):
    from importlib import import_module

    return import_module(name)


if _has_jinja:
    if _has_pass_context:
        @jinja2.pass_context
        def python_eval(ctx, code):
            return eval(code, ctx.parent, ctx.vars)


        @jinja2.pass_context
        def python_exec(ctx, code):
            from PyFoam.ThirdParty.six import exec_

            result = exec_(code, ctx.parent, ctx.vars)
            return result


def get_jinja_environment(strict_undefined=True, allow_execute=False):
    global _environments

    spec = (strict_undefined, allow_execute)

    if _has_jinja:
        # provoke raising the import error we had before
        import jinja2

    if spec not in _environments:
        if strict_undefined:
             undefined = jinja2.StrictUndefined
        else:
             undefined = jinja2.Undefined

        _environment = jinja2.Environment(undefined=undefined)
        _environment.filters["parse_foam_file"] = parse_foam_file
        _environment.filters["parse_foam"] = parse_foam_string
        _environment.filters["format_foam"] = format_foam
        _environment.filters["import_module"] = import_module
        _environment.filters["solution_dir"] = solution_dir
        if _has_pass_context:
            _environment.filters["python_eval"] = python_eval
            if allow_execute:
                _environment.filters["python_exec"] = python_exec

            try:
                _environment.add_extension("jinja2.ext.do")
            except AttributeError:
                pass

        _environments[spec] = _environment

    return _environments[spec]
