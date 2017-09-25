import xml.etree.ElementTree as ET
import re
import json
import logging
import sys, os
import glob

logger = logging.getLogger(__name__)

# Attribute Registry Convertor
#   .xml to .json file converter

class AttribRegistry(object):

    def _sanitize_name(self, fld_name, suffix):
        typName = fld_name.strip() + suffix
        typName = re.sub('^(^[0-9])', 'E_\\1', typName)
        typName = re.sub('[[]([^]:]+)[^]]*[]]', '\\1', typName)
        typName = re.sub('[?]', '', typName)
        typName = re.sub('[-.]', '_', typName)
        typName = re.sub('^[ \t]+', '', typName)
        return typName
    def __init__(self, file_name):
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        regentry = None
        for regent in self.root:
            if regent.tag == "REGISTRY_ENTRIES":
                regentry = regent
                break
        self.comp = re.sub("^.*[\\\\]", "", file_name)
        self.comp = re.sub("\..*$", "", self.comp)
        self.addGroup = re.match('iDRAC', self.comp)
        self.direct = re.sub("[^\\\\]+$", "", file_name)
        self.attr_json = {
            "$schema" : file_name,
            "title" : file_name,
            "$ref" : "#/definitions/" + self.comp,
            "definitions" : {
                self.comp : {
                    "config_groups" : {},
                    "type" : "object",
                    "properties" : {}
                }
            }
        }

        attmap = {
            'IsReadOnly' : 'readonly',
            'DisplayName' : 'description',
            'HelpText' : 'longDescription',
            'Partition' : 'partition',
            'RegEx' : 'pattern',
            'GroupName' : 'qualifier',
            'AttributeName' : 'name',
            'AttributeType' : 'baseType',
            'DefaultValue' : 'default',
        }
        typemaps = {
            'integer' : 'int',
            'string' : 'str',
            'enumeration' : 'enum',

            'orderlistseq' : 'list',
            'password' : 'str',
            'binary' : 'str',
            'minmaxrange' : 'int',
            'range' : 'int'
        }
        attrx_group = {}
        all_entries = []
        for attr in regentry:
            myentry = {}
            for attrfield in attr:
                if len(attrfield) <= 0:
                    # attribute
                    myentry [attrfield.tag] = attrfield.text
                    if attrfield.tag in ["GroupName"]:
                        if not attrfield.text in attrx_group:
                            attrx_group[attrfield.text] = []
                        attrx_group[attrfield.text].append(myentry)
                elif attrfield.tag in ["AttributeType"]:
                    if not attrfield.tag in myentry:
                        myentry[attrfield.tag] = {}
                    myentry [attrfield.tag] = attrfield.text
                elif attrfield.tag in ["AttributeValue"]:
                    if not attrfield.tag in myentry:
                        myentry[attrfield.tag] = {}
                        myentry["enum"] = []
                        myentry["enumDescriptions"] = []
                    enum_name = None
                    enum_value = None
                    for child in attrfield:
                        if (child.tag == "ValueName"):
                            if enum_value:
                                logger.debug("WARN: Duplicate value found!")
                            else:
                                enum_value = child.text
                        else:
                            if enum_name:
                                logger.debug("WARN: Duplicate name found!")
                            else:
                                enum_name = child.text
                    myentry[attrfield.tag][enum_name] = enum_value
                    myentry["enum"].append(enum_value.strip())
                    myentry["enumDescriptions"].append(enum_name)
                elif attrfield.tag in ["Modifiers"]:
                    for modifiers in attrfield:
                        if modifiers.tag in ['BrowserRead', 'BrowserWrite',
                                'BrowserSuppressed', 'ProgrammaticRead',
                                'ProgrammaticWrite']:
                            pass
                        elif modifiers.tag in ['RegEx', 'Partition']:
                            myentry[modifiers.tag] = modifiers.text
                        else:
                            logger.debug("WARN: Unknown!!" + modifiers.tag)
                else:
                    logger.debug("WARN: Unknown!!" + attrfield.tag)
            all_entries.append(myentry)
        for group in attrx_group:
            tt = self.attr_json["definitions"][self.comp]["config_groups"]
            tt[group] = []
            for ent in attrx_group[group]:
                fld_name = ent["AttributeName"]
                if self.addGroup:
                    fld_name += "_" + group
                tt[group].append(fld_name)

        for entry in all_entries:
            tt = self.attr_json["definitions"][self.comp]["properties"]
            if entry['AttributeType'].lower() in [
                'form title', 'form ref', 'checkbox', 'formset title'
            ]: continue

            fld_name = entry["AttributeName"]
            if self.addGroup and "GroupName" in entry:
                fld_name = fld_name + "_" + entry["GroupName"]
            tt[fld_name] = {}
            for fld in attmap:
                if fld in entry:
                    if attmap[fld] in ['baseType']:
                        ntype = typemaps[entry[fld].lower()]
                        tt[fld_name][attmap[fld]] = ntype
                    else:
                        tt[fld_name][attmap[fld]] = entry[fld]
            attr_type = 'string'
            if "AttributeType" in entry:
                attr_type = entry["AttributeType"].lower()
            if "AttributeValue" in entry:
                typName = self._sanitize_name(fld_name, 'Types')
                tt[fld_name]["type"] = typName
                self.attr_json["definitions"][typName] = {
                    "enum" : entry["enum"],
                    "enumDescriptions" : entry["enumDescriptions"],
                    "type" : attr_type,
                }

        props = self.attr_json["definitions"][self.comp]["properties"]
        if 'StripeSize' in props:
            props['StripeSize']['type'] = 'StripeSizeTypes'
            self.attr_json["definitions"]['StripeSizeTypes'] = {
                "enum": [
                    "Default",
                    "512",
                    "1KB", "2KB", "4KB", "8KB",
                    "16KB", "32KB", "64KB",
                    "128KB", "256KB", "512KB",
                    "1MB", "2MB", "4MB", "8MB",
                ],
                "enumDescriptions": [
                    "Default",
                    "512",
                    "1KB", "2KB", "4KB", "8KB",
                    "16KB", "32KB", "64KB",
                    "128KB", "256KB", "512KB",
                    "1MB", "2MB", "4MB", "8MB",
                ],
                "type": "string"
            }
    def save_file(self, directory = None, filename = None):
        if not directory: directory = self.direct
        if not filename: filename = self.comp + ".json"
        dest_file = os.path.join(directory, filename)
        print ("Saving to :" + dest_file)
        with open(dest_file, "w") as out:
            out.write(json.dumps(self.attr_json, sort_keys=True,
                                 indent=4, separators=(',', ': ')))

    def save_enums(self, directory = None, filename = None):
        if self.comp == 'EventFilters': return
        if not directory: directory = self.direct
        if not filename: filename = self.comp + ".py"
        dest_file = os.path.join(directory, filename)
        print('Saving to :' + dest_file)
        with open(dest_file, 'w') as out:
            out.write('from omsdk.sdkcenum import EnumWrapper\n')
            out.write('import logging\n')
            out.write('\n')
            out.write('logger = logging.getLogger(__name__)\n')
            out.write('\n')
            props = self.attr_json
            sprops = []
            for i in props['definitions']:
                if 'enum' not in props['definitions'][i]:
                    continue
                sprops.append(i)
            sprops = sorted(sprops)

            for i in sprops:
                en_val = [k.strip() for k in props['definitions'][i]['enum']]
                en_name = []
                out.write('{0} = EnumWrapper("{0}", '.format(i) + '{\n')
                MBLOOKUP = {
                  '1KB' : 1*1024,
                  '2KB' : 2*1024,
                  '4KB' : 4*1024,
                  '8KB' : 8*1024,
                  '16KB' : 16*1024,
                  '32KB' : 32*1024,
                  '64KB' : 64*1024,
                  '128KB' : 128*1024,
                  '256KB' : 256*1024,
                  '512KB' : 512*1024,
                  '1MB' : 1*1024*1024,
                  '2MB' : 2*1024*1024,
                  '4MB' : 4*1024*1024,
                  '8MB' : 8*1024*1024,
                  'Default' : 'Default',
                  '512' : '512',
                }

                for ent in en_val:
                    en_name.append(self._sanitize(ent))
                if i == 'StripeSizeTypes':
                    t_en_val = []
                    for ent in en_val:
                        t_en_val.append(MBLOOKUP[ent])
                    en_val = t_en_val
                en_dict = dict(zip(en_name, en_val))
                snames = sorted([i for i in en_dict])
                for j in snames:
                    out.write('    "{0}" : "{1}",\n'.format(j, en_dict[j]))
                out.write('}).enum_type\n')
                out.write('\n')

    def _sanitize(self, tval):
        if tval:
            tval = re.sub('[^A-Za-z0-9]', '_', tval)
            tval = re.sub('[^A-Za-z0-9]', '_', tval)
            tval = re.sub('^(True|None|False)$', 'T_\\1', tval)
            tval = re.sub('^(^[0-9])', 'T_\\1', tval)
        return tval

    def _print(self, out, props, group, dconfig):

        # build groups!!
        new_prop_def = {}
        # group
        #   fldname
        #    ::pytype
        #        modDeleteAllowed
        #        uneditable
        #        doc
        #        type
        #        default
        #        alias
        FieldTypeMap = {
                'enum' : 'EnumTypeField',
                'str' : 'StringField',
                'int' : 'IntField',
                'bool' : 'BooleanField',
                'enum' : 'EnumTypeField',
                'list' : 'StringField', # TODO
        }
        js = { self.comp : { "groups" : sorted(new_prop_def.keys()) }}
        if group:
            config_spec = os.path.join(dconfig, self.comp + '.comp_spec')
            if os.path.exists(config_spec):
                with open(config_spec) as f:
                    js = json.load(f)

        for i in props:
            if group: gname = props[i]['qualifier']
            else: gname = self.comp
            if not gname in new_prop_def:
                new_prop_def[gname] = {}
            if not i in new_prop_def[gname]:
                new_prop_def[gname][i] = {}

            # readonly, unediable 
            new_prop_def[gname][i]['modDeleteAllowed'] = True
            new_prop_def[gname][i]['uneditable'] = False
            if 'readonly' in props[i] and \
                props[i]['readonly'].lower() in ['true']:

                if 'longDescription' in props[i] and \
                    'Configurable via XML' not in props[i]['longDescription']:
                    new_prop_def[gname][i]['uneditable'] = True

                new_prop_def[gname][i]['modDeleteAllowed'] = False

            # Pydoc description
            desc = i
            if 'longDescription' in props[i]:
                desc = props[i]['longDescription']
            desc = re.sub('[ \t\v\b]+', ' ', desc)
            desc = re.sub('[^[A-Za-z0-9;,.<>/:!()]" -]', "", desc)
            desc = desc.replace('"', "'")
            new_prop_def[gname][i]['doc'] = desc

            # python type
            f_pytype = FieldTypeMap[props[i]['baseType']]

            # Default processing
            if 'default' not in props[i]:
                props[i]['default'] = None

            # type and default values
            new_prop_def[gname][i]['type'] = None
            new_prop_def[gname][i]['default'] = props[i]['default']
            defval = new_prop_def[gname][i]['default']

            if defval:
                typename = None
                if 'type' in props[i]:
                    typename = props[i]['type']
                    if typename in self.attr_json["definitions"]:
                        typedef = self.attr_json['definitions'][typename]
                        if 'enum' not in typedef:
                            pass
                            #print(self.comp+'.'+typename+ ' has no enums!')
                        elif defval not in typedef['enum']:
                            typedef['enum'].append(defval)
                            typedef["enumDescriptions"].append(defval)
                            #print(defval+" added to " + self.comp+'.'+typename)
                        if len(typedef['enum']) <= 1:
                            #print(i + " is suspcious enum. has one entry!")
                            f_pytype = 'StringField'
                        elif f_pytype not in ['EnumTypeField']:
                            #print(props[i]['baseType']+" wrong enum:" + i)
                            f_pytype = 'EnumTypeField'

            if f_pytype in ['EnumTypeField']:
                if 'type' not in props[i]:
                    #print(i + " is wrong typed as enum. switching to enum!")
                    f_pytype = 'StringField'

            #if o_pytype != f_pytype:
            #    print("{0} => original({1}), new({2})".format(i, o_pytype, f_pytype))

            if f_pytype in ['EnumTypeField']:
                if defval:
                    defval = props[i]['type'] + '.' + self._sanitize(defval)
                else:
                    defval = str(defval)
                new_prop_def[gname][i]['type'] = props[i]['type']
            else:
                if defval:
                    defval = '"' + defval + '"'
                else:
                    defval = str(defval)
                field_spec = defval
            new_prop_def[gname][i]['default'] = defval
            new_prop_def[gname][i]['pytype'] = f_pytype

            # alias:
            new_prop_def[gname][i]['alias'] = None
            new_prop_def[gname][i]['fldname'] = self._sanitize_name(i, '')
            if new_prop_def[gname][i]['fldname'] != i.strip():
                new_prop_def[gname][i]['alias'] = i

        for grp in sorted(new_prop_def.keys()):
            cls_props = list(new_prop_def[grp].keys())
            s_cls_props = sorted([i for i in cls_props])
            ngrp = self._sanitize(grp)
            out.write('class {0}(ClassType):\n'.format(ngrp))
            out.write('\n')
            out.write('    def __init__(self, parent = None):\n')
            if grp == self.comp:
                out.write('        super().__init__("Component", None, parent)\n')
            else:
                out.write('        super().__init__(None, "'+grp+'", parent)\n')
            for i in s_cls_props:
                if '[Partition:n]' in i:
                    continue
                field_spec = "        self.{0} = ".format(new_prop_def[grp][i]['fldname'])
                field_spec  += "{0}({1}".format(new_prop_def[grp][i]['pytype'], new_prop_def[grp][i]['default'])
                if new_prop_def[grp][i]['type']:
                    field_spec  += ",{0}".format(new_prop_def[grp][i]['type'])
                if new_prop_def[grp][i]['alias']:
                    field_spec += ', alias="{0}"'.format(new_prop_def[grp][i]['alias'])
                field_spec += ', parent=self'
                if not new_prop_def[grp][i]['modDeleteAllowed']:
                    field_spec += ", modifyAllowed = False"
                    field_spec += ", deleteAllowed = False"
                if new_prop_def[grp][i]['uneditable']:
                    out.write('        # readonly attribute populated by iDRAC\n')
                elif not new_prop_def[grp][i]['modDeleteAllowed']:
                    out.write('        # readonly attribute\n')
                out.write(field_spec + ')\n')
            out.write('        self.commit()\n')
            out.write('\n')
            if 'arrays' in js and grp in js['arrays']:
                ent = js['arrays'][grp]
                if 'key' not in ent:
                    print("ERROR: Key is not present for "+ grp)
                    ent['key'] = [ grp ]
                out.write('    @property\n')
                out.write('    def Key(self):\n')
                fmsg = ""
                comma = ""
                for field in ent['key']:
                    fmsg += comma + 'self.' + field + '_' + grp
                    comma = ", "
                if ',' in fmsg:
                    fmsg = '(' + fmsg + ')'
                out.write('        return {0}\n'.format(fmsg))
                out.write('\n')
                out.write('    @property\n')
                out.write('    def Index(self):\n')
                out.write('        return self.{0}_{1}._index\n'.format(ent['key'][0], grp))
                out.write('\n')
        if group:
            js = { self.comp : { "groups" : sorted(new_prop_def.keys()) }}
            config_spec = os.path.join(dconfig, self.comp + '.comp_spec')
            if os.path.exists(config_spec):
                with open(config_spec) as f:
                    js = json.load(f)
            for comp in js:
                if 'registry' not in js[comp] or \
                   js[comp]['registry'] != self.comp:
                    continue
                if 'groups' not in js[comp]:
                    js[comp]['groups'] = []
                if 'excl_groups' in js[comp]:
                    grps = set(js[comp]['groups']+ list(new_prop_def.keys()))
                    grps = grps - set(js[comp]['excl_groups'])
                    js[comp]['groups'] = grps
                if len(js[comp]['groups']) <= 0:
                    continue
                out.write('class {0}(ClassType):\n'.format(comp))
                out.write('\n')
                out.write('    def __init__(self, parent = None):\n')
                out.write('        super().__init__("Component", None, parent)\n')
                for grp in sorted(js[comp]['groups']):
                    ngrp = self._sanitize(grp)
                    if 'arrays' in js and grp in js['arrays']:
                        ent = js['arrays'][grp]
                        out.write('        self.{0} = ArrayType({0}, parent=self, min_index={1}, max_index={2})\n'.format(ngrp, ent['min'], ent['max']))


                    else:
                        out.write('        self.{0} = {0}(parent=self)\n'.format(ngrp))

                out.write('        self.commit()\n')
                out.write('\n')

    def save_types(self, directory, dconfig, group):
        if self.comp == 'EventFilters': return
        if not directory: directory = self.direct
        filename = self.comp + ".py"
        dest_file = os.path.join(directory, filename)
        print('Saving to :' + dest_file)
        self.device = 'iDRAC'

        with open(dest_file, 'w') as out:
            props = self.attr_json['definitions'][self.comp]['properties']
            out.write('from omdrivers.enums.{0}.{1} import *\n'.format(self.device, self.comp))
            out.write('from omsdk.typemgr.ClassType import ClassType\n')
            out.write('from omsdk.typemgr.ArrayType import ArrayType\n')
            out.write('from omsdk.typemgr.BuiltinTypes import *\n')
            out.write('import logging\n')
            out.write('\n')
            out.write('logger = logging.getLogger(__name__)\n')
            out.write('\n')

            self._print(out, props, group, dconfig)

if __name__ == "__main__":
    driver_dir = os.path.join('omdrivers', 'iDRAC')
    for file1 in glob.glob(os.path.join(driver_dir, "xml", "*.xml")):
        if file1.endswith('EventFilters.xml') is True: continue
        grp = file1.endswith('iDRAC.xml')
        ar= AttribRegistry(file1)
        ar.save_file(directory=os.path.join(driver_dir, 'Config'))
        ar.save_types(directory=os.path.join('omdrivers', 'types', 'iDRAC'),
                      dconfig =os.path.join(driver_dir, 'Config'),
                      group=grp)
        # types would have added unknown enumerations!
        ar.save_enums(directory=os.path.join('omdrivers', 'enums', 'iDRAC'))
