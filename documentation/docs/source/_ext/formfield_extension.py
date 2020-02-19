# Custom FormField Extension

# resources
# https://www.bustawin.com/sphinx-extension-devel/
# http://www.xavierdupre.fr/blog/2015-06-07_nojs.html
# http://www.sphinx-doc.org/en/master/extdev/index.html#dev-extensions
# https://www.sphinx-doc.org/en/master/development/tutorials/todo.html
# https://www.sphinx-doc.org/en/master/extdev/appapi.html

# imports
from docutils import nodes
from docutils.parsers.rst import Directive, directives


def validate_deonticity_choice(argument):
    """
    """
    return directives.choice(argument, ('required', 'optional', 'complete_for'))

class FormFieldNode(nodes.Structural, nodes.Element):
    pass

class FormFieldDirective(Directive):
    """
    """
    required_arguments = 2
    optional_arguments = 1
    has_content = True

    def run(self):
        form_field = self.arguments[0]
        deonticity = validate_deonticity_choice(self.arguments[1])

        section = nodes.section(ids=nodes.make_id('formfield'))
        section += nodes.title(form_field)
        section += nodes.paragraph(self.content)

        return [section]

def setup(app):
     app.add_config_value('include_formfield', False, 'html')
     app.add_node(FormFieldNode)
     app.add_directive('formfield', FormFieldDirective)
