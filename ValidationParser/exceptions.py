

class ParsingError(Exception):

    def __init__(self, results, *args):
        self.results = results
        super().__init__(*args)

    def __str__(self):
        return 'ERROR: Parsing Error: %r' % self.results

    def __repr__(self):
        return str(self)


class ParsingLocalError(ParsingError):
    def __str__(self):
        return 'ERROR: Local Parsing Error: %r' % self.results


class ParsingFatalError(ParsingError):
    def __str__(self):
        return 'ERROR: Fatal Parsing Error: %r' % self.results


class MessageNotFoundError(Exception):

    def __init__(self, msg_key, message_lookup=None):
        self.msg_key = msg_key
        self.message_lookup = message_lookup

    @property
    def _get_keys(self):
        # tmp_segment_key = '%s.*' % self.msg_key.seg_key
        tmp_items = [item.key for item in self.message_lookup.iter_messages(self.msg_key.seg_key)]
        return ', '.join(tmp_items)

    def __str__(self):
        return 'ERROR: Message %s not found.  Keys in segment = [%r]' % (self.msg_key, self._get_keys)

    def __repr__(self):
        return str(self)


class SegmentNotFoundError(Exception):

    def __init__(self, msg_key, message_lookup=None):
        try:
            self.msg_key = msg_key.seg_key
        except AttributeError:
            self.msg_key = msg_key
        self.message_lookup = message_lookup

    @property
    def _get_keys(self):
        if self.message_lookup is None:
            return '<no message lookup passed>'
        try:
            tmp_items = self.message_lookup.segments.keys()
        except Exception as err:
            return "Error reading message lookup: %s" % err

        return ', '.join(tmp_items)

    def __str__(self):
        return 'ERROR: Segment %s not found.  Segments available = [%s]' % (self.msg_key, self._get_keys)

    def __repr__(self):
        return str(self)


class ReferenceNotFoundError(Exception):
    def __init__(self, ref_key, message_lookup=None):
        self.ref_key = ref_key
        self.message_lookup = message_lookup

    @property
    def _get_keys(self):
        if self.message_lookup is None:
            return '<no mesage lookup passed>'
        tmp_items = self.message_lookup.references.keys()
        return ', '.join(tmp_items)

    def __str__(self):
        return 'ERROR: Reference %s not found.  References available = %r' % (self.ref_key, self._get_keys)

    def __repr__(self):
        return str(self)




# class WrapperStop(Exception):
#
#     def __init__(self, wrapper, results, *args):
#        self.wrapper = wrapper
#        self.results = results
#        super().__init__(*args)
#
#     def __str__(self):
#         return 'Wrapper [%s] raised a stop Error for: %s' % (self.wrapper.name, self.results)
#
#     def __repr__(self):
#         return str(self)


# class UnfinishedParsing(Exception):
#     def __str__(self):
#         return 'ERROR: Not finished parsing yet, data is not available'


class MessageListLocked(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        super().__init__(*args)

    def __str__(self):
        return 'ERROR: unable to add %s, message list locked' % self.msg
