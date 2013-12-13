# -*- coding: utf-8 -*-
import logging
import functools

from django.conf import settings
from django.core.management.base import BaseCommand, make_option
from django.template.base import Node
from django.template.loader import get_template
from django.template.context import Context

from django.utils.encoding import force_unicode

logger = logging.getLogger(__name__)


def patch_template(template, out_file):
    def file_render(self, out_file, context):
        bits = out_file
        for node in self:
            if isinstance(node, Node):
                bit = self.render_node(node, context)
            else:
                bit = node
            bit = force_unicode(bit)
            bits.write(bit.encode('utf-8'))
        return 'rendered to file %s' % out_file

    template.nodelist.render = functools.partial(file_render, template.nodelist, out_file)
    return template


def render_to_file(out_file, template_name, context=None):
    # chuncked render to file
    template = get_template(template_name)

    patched_template = patch_template(template, out_file)

    if context is None:
        context=Context()

    try:
        template.render(context=context)
    finally:
        del template.nodelist.render
