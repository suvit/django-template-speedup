# -*- coding: utf-8 -*-
import logging
import functools

from django.conf import settings
from django.core.management.base import BaseCommand, make_option
from django.template.base import Node, NodeList, VariableDoesNotExist
from django.template.loader import get_template
from django.template.defaulttags import IfNode, ForNode, WithNode
from django.template.context import Context

from django.utils.encoding import force_unicode

logger = logging.getLogger(__name__)


class FileNodeList(object):
    def __init__(self, nodelist, outfile):
        self.nodelist = nodelist
        self.outfile = outfile

    def __iter__(self):
        return iter(self.nodelist)

    def render_for(nodelist, self, context):
        if 'forloop' in context:
            parentloop = context['forloop']
        else:
            parentloop = {}
        context.push()
        try:
            values = self.sequence.resolve(context, True)
        except VariableDoesNotExist:
            values = []
        if values is None:
            values = []
        if not hasattr(values, '__len__'):
            values = list(values)
        len_values = len(values)
        if len_values < 1:
            context.pop()
            return self.nodelist_empty.render(context)
        if self.is_reversed:
            values = reversed(values)
        unpack = len(self.loopvars) > 1
        # Create a forloop value in the context.  We'll update counters on each
        # iteration just below.
        loop_dict = context['forloop'] = {'parentloop': parentloop}
        for i, item in enumerate(values):
            # Shortcuts for current loop iteration number.
            loop_dict['counter0'] = i
            loop_dict['counter'] = i+1
            # Reverse counter iteration numbers.
            loop_dict['revcounter'] = len_values - i
            loop_dict['revcounter0'] = len_values - i - 1
            # Boolean values designating first and last times through loop.
            loop_dict['first'] = (i == 0)
            loop_dict['last'] = (i == len_values - 1)

            pop_context = False
            if unpack:
                # If there are multiple loop variables, unpack the item into
                # them.
                try:
                    unpacked_vars = dict(zip(self.loopvars, item))
                except TypeError:
                    pass
                else:
                    pop_context = True
                    context.update(unpacked_vars)
            else:
                context[self.loopvars[0]] = item
            # In TEMPLATE_DEBUG mode provide source of the node which
            # actually raised the exception
            if settings.TEMPLATE_DEBUG:
                for node in self.nodelist_loop:
                    try:
                        FileNodeList(node, nodelist.outfile).render(context)
                    except Exception, e:
                        if not hasattr(e, 'django_template_source'):
                            e.django_template_source = node.source
                        raise
            else:
                for node in self.nodelist_loop:
                    FileNodeList(node, nodelist.outfile).render(context)
            if pop_context:
                # The loop variables were pushed on to the context so pop them
                # off again. This is necessary because the tag lets the length
                # of loopvars differ to the length of each set of items and we
                # don't want to leave any vars from the previous loop on the
                # context.
                context.pop()
        context.pop()
        return u''

    def render_node(self, node, context):
        return node.render(context)

        # TODO
        if isinstance(node, IfNode):
            new_cn = []
            for condition, nodelist in node.conditions_nodelists:
                new_cn.append((condition, FileNodeList(nodelist, self.outfile)))
            node.conditions_nodelists = new_cn
        elif isinstance(node, ForNode):
            return self.render_for(node, context)
        elif isinstance(node, WithNode):
            node.nodelist = FileNodeList(node.nodelist, self.outfile)

        return node.render(context)

    def render(self, context):
        for node in self:
            if isinstance(node, Node):
                bit = self.render_node(node, context)
            else:
                bit = node
            bit = force_unicode(bit)
            self.outfile.write(bit.encode('utf-8'))
        return ''


def patch_template(template, out_file):

    template.nodelist = FileNodeList(template.nodelist, out_file)
    return template


def render_to_file(out_file, template_name, context=None):
    # chuncked render to file
    template = get_template(template_name)

    if context is None:
        context = Context()

    patched_template = patch_template(template, out_file)
    try:
        patched_template.render(context=context)
    finally:
        del patched_template.nodelist
