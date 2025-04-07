"""
Class that implements the common functionality for the format of templates
"""
from optparse import OptionGroup

from PyFoam import configuration as config

class CommonTemplateFormat(object):
    """ The class that defines options for template formats
    """

    def addOptions(self):
        from PyFoam.Basics.TemplateFile import available_engines

        gformat = OptionGroup(self.parser,
                              "Template Format",
                              "General settings for all template formats")
        gformat.add_option("--template-engine-default",
                           type="choice",
                           choices=available_engines(),
                           default=config().get("Template","defaultEngine"),
                           dest="templateDefaultEngine",
                           help="The templating engine that should be used. Available engines are " \
                             + ", ".join(available_engines()) + " where 'auto' tries to determine the engine automatically. Default: %default")
        gformat.add_option("--peek-lines-for-auto",
                           action="store",
                           type=int,
                           default=5,
                           dest="peekLinesAuto",
                           help="How many lines to peek into the file to detect the templating engine to use. Default: %default")
        gformat.add_option("--fallback-template-engine",
                           type="choice",
                           choices=available_engines(no_auto=True),
                           default=config().get("Template","fallbackEngine"),
                           dest="fallbackDefaultEngine",
                           help="The templating engine that should be used if 'auto' can not determine it. Available engines are " \
                             + ", ".join(available_engines(no_auto=True)) + ". Default: %default")

        self.parser.add_option_group(gformat)
        tformat = OptionGroup(self.parser,
                              "Pyratemp Format",
                              "Specifying details about the format of the pyratemp-templates (new format)")
        self.parser.add_option_group(tformat)
        tformat.add_option("--expression-delimiter",
                           action="store",
                           default=config().get("Template","expressionDelimiter"),
                           dest="expressionDelimiter",
                           help="String that delimits an expression. At the end of the expression the reverse string is being used. Default: %default")
        tformat.add_option("--assignment-line-start",
                           action="store",
                           default=config().get("Template","assignmentLineStart"),
                           dest="assignmentLineStart",
                           help="String at the start of a line that signifies that this is an assignment. Default: %default")
