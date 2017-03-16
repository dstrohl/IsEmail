
import xml.etree.ElementTree as ET
import textwrap

ISEMAIL_META_FILENAME = 'meta.xml'
ISEMAIL_WRAPPERS = {}

def wrap_and_indent(str_in, indent=0, bullet='', width=80):

    lookup = 'I:%s-B:%s-W:%s' % (indent, bullet, width)

    if lookup in ISEMAIL_WRAPPERS:
        wrapper = ISEMAIL_WRAPPERS[lookup]
    else:
        init_indent = '%s%s' % (' '.ljust(indent), bullet)
        sub_indent = ' '.ljust(len(init_indent))
        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=init_indent,
            subsequent_indent=sub_indent,
            tabsize=4,)
        ISEMAIL_WRAPPERS[lookup] = wrapper

    tmp_ret = wrapper.wrap(str_in)

    return '\n'.join(tmp_ret)



class IsEmailMetaItemClass(object):

    def __init__(self, item_dict):
        self._data = item_dict
        self._id = None
        self._cat_id = None
        self._name = None
        self._str_cache = {}

    @property
    def id(self):
        if self._id is None:
            tmp_diag_id = self._data['id'][8:]

            if tmp_diag_id.startswith(self.cat_id):
                self._id = tmp_diag_id[len(self.cat_id):]
            else:
                self._id = tmp_diag_id
        return self._id

    @property
    def cat_id(self):
        if self._cat_id is None:
            self._cat_id = self._data['category']['id'][8:]
        return self._cat_id

    @property
    def name(self):
        return '%s / %s' % (self.cat_id, self.id)

    def diag_desc(self, indent=4, width=80, bullet='-'):
        lookup = '%s-%s-%s-%s' % ('diag', indent, width, bullet)
        if lookup not in self._str_cache:
            tmp_str = wrap_and_indent(self._data['desc'], indent=indent, width=width, bullet=bullet)
            self._str_cache[lookup] = tmp_str
        return self._str_cache[lookup]

    def cat_desc(self, indent=4, width=80, bullet='-'):
        lookup = '%s-%s-%s-%s' % ('cat', indent, width, bullet)
        if lookup not in self._str_cache:
            tmp_str = wrap_and_indent(self._data['category']['desc'], indent=indent, width=width, bullet=bullet)
            self._str_cache[lookup] = tmp_str
        return self._str_cache[lookup]

    def short_string(self, indent=4, width=80, bullet='- '):
        """
        should return:

            RFC5321 / QUOTEDSTRING:
                - Address is valid for SMTP but has unusual elements
                - Address is valid but contains a quoted string
        """
        short_str_format = '{name}:\n{cat_desc}\n{desc}\n'

        return short_str_format.format(
            name=self.name,
            desc=self.diag_desc(indent=indent, width=width, bullet=bullet),
            cat_desc=self.cat_desc(indent=indent, width=width, bullet=bullet))

    def __repr__(self):
        return 'IS Email Metadata: %s' % self._data['id']


class IsEmailMetaData(object):
    def __init__(self):
        self.diags = {}
        self.diag_ids = {}
        self.cats = {}
        self.refs = {}
        self.smtp_errs = {}
        self.loaded = False

    def _load(self):
        if not self.loaded:
            meta_root = ET.parse(ISEMAIL_META_FILENAME).getroot()

            for item in meta_root:
                if item.tag == 'Categories':
                    for cat in item:
                        id = cat.get('id')
                        self.cats[id] = dict(
                            id=id,
                            value=int(cat.find('value').text),
                            desc=cat.find('description').text,
                        )

                elif item.tag == 'SMTP':
                    for smtp in item:
                        id = smtp.get('id')
                        self.smtp_errs[id] = dict(
                            id=id,
                            value=smtp.find('value').text,
                            text=smtp.find('text').text,
                        )

                elif item.tag == 'References':
                    for ref in item:
                        id = ref.get('id')
                        self.refs[ref.get('id')] = dict(
                            id=id,
                            blockquote=ref.find('blockquote').text,
                            cite=ref.find('cite').text,
                        )

                elif item.tag == 'Diagnoses':
                    for diag in item:
                        id = diag.get('id')
                        tmp_dict = dict(
                            id=id,
                            value=int(diag.find('value').text),
                            category=self.cats[diag.find('category').text],
                            smtp=self.smtp_errs[diag.find('smtp').text],

                            desc=diag.find('description').text,
                            references=[],
                        )
                        for ref in diag.findall('reference'):
                            tmp_dict['references'].append(self.refs[ref.text])

                        self.diags[id] =tmp_dict
                        self.diag_ids[int(diag.find('value').text)] = tmp_dict

            self.loaded = True

    def __getitem__(self, item):
        self._load()
        if isinstance(item, int):
            return IsEmailMetaItemClass(self.diag_ids[item])
        else:
            return IsEmailMetaItemClass(self.diags[item])

