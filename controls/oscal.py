import os
import json
import yaml
import re
from pathlib import Path

CATALOG_PATH = os.path.join(os.path.dirname(__file__),'data','catalogs')


class Catalogs (object):
    """Represent list of catalogs"""
    def __init__(self):
        global CATALOG_PATH
        self.catalog_path = CATALOG_PATH
        # self.catalog = None
        self.catalog_keys = self._list_catalog_keys()
        self.index = self._build_index()

    def _list_catalog_files(self):
        return [
            'NIST_SP-800-53_rev4_catalog.json',
            'NIST_SP-800-53_rev5_catalog.json'
        ]

    def _list_catalog_keys(self):
        return [
            'NIST_SP-800-53_rev4',
            'NIST_SP-800-53_rev5'
        ]

    def _load_catalog_json(self, catalog_key):
        catalog = Catalog(catalog_key)
        # print(catalog_key, catalog._load_catalog_json())
        return catalog._load_catalog_json()

    def _build_index(self):
        """Build a small catalog_index from metada"""
        index = []
        for catalog_key in self._list_catalog_keys():
            catalog = self._load_catalog_json(catalog_key)
            index.append( { 'id': catalog['id'], 'catalog_key': catalog_key, 'catalog_key_display': catalog_key.replace("_", " "), 'metadata': catalog['metadata'] } )
        return index

    def list(self):
        catalog_titles = [item['metadata']['title'] for item in self.index ]
        return catalog_titles

class Catalog (object):
    """Represent a catalog"""

    # Create a singleton instance of this class. GetInstance returns
    # that singleton instance. Instead of doing `cg = Catalog()`,
    # do `cg = Catalog.GetInstance()`.
    @staticmethod
    def GetInstance(catalog_key='NIST_SP-800-53_rev4'):
        # Create a new instance of Catalog() the first time
        # this method is called. Keep it in memory indefinitely.
        if not hasattr(Catalog, '_cached_instance'):
            Catalog._cached_instance = Catalog(catalog_key=catalog_key)
        return Catalog._cached_instance

    def __init__(self, catalog_key='NIST_SP-800-53_rev4'):
        global CATALOG_PATH
        self.catalog_key = catalog_key
        self.catalog_key_display = catalog_key.replace("_", " ")
        self.catalog_path = CATALOG_PATH
        self.catalog_file = catalog_key + "_catalog.json"
        try: 
            self.oscal = self._load_catalog_json()
            self.status = "ok"
            self.status_message = "Success loading catalog"
            self.catalog_id = self.oscal['id']
            self.info = {}
            self.info['groups'] = self.get_groups()
        except Exception as e:
            self.oscal = None
            self.status = "error"
            self.status_message = "Error loading catalog"
            self.catalog_id = None
            self.info = {}
            self.info['groups'] = None

    def _load_catalog_json(self):
        """Read catalog file - JSON"""
        catalog_file = os.path.join(self.catalog_path, self.catalog_file)
        # Does file exist?
        if not os.path.isfile(catalog_file):
            print("ERROR: {} does not exist".format(catalog_file))
            return False
        # Load file as json
        with open(catalog_file, 'r') as json_file:
            data = json.load(json_file)
            oscal = data['catalog']
        return oscal

    def find_dict_by_value(self, search_array, search_key, search_value):
        """Return the dictionary in an array of dictionaries with a key matching a value"""
        result_dict = next((sub for sub in search_array if sub[search_key] == search_value), None)
        return result_dict

    # def ids(self, search_collection):
    #     """Return the array of ids for a collection"""
    #     return [item['id'] for item in search_collection if 'id' in item]

    def get_groups(self):
        return self.oscal['groups']

    def get_group_ids(self):
        search_collection = self.get_groups()
        return [item['id'] for item in search_collection]

    def get_group_title_by_id(self, id):
        group = self.find_dict_by_value(self.get_groups(), 'id', id)
        return group['title']

    def get_controls(self):
        controls = []
        for group in self.get_groups():
            controls += [control for control in group['controls']]
        return controls

    def get_control_ids(self):
        search_collection = self.get_controls()
        return [item['id'] for item in search_collection]

    def get_controls_all(self):
        controls = []
        for group in self.get_groups():
            for control in group['controls']:
                controls.append(control)
                if 'controls' in control:
                    controls += [control_e for control_e in control['controls']]
        return controls

    def get_controls_all_ids(self):
        search_collection = self.get_controls_all()
        return [item['id'] for item in search_collection]

    def get_control_by_id(self, control_id):
        """Return the dictionary in an array of dictionaries with a key matching a value"""
        search_array = self.get_controls_all()
        search_key = 'id'
        search_value = control_id
        result_dict = next((sub for sub in search_array if sub[search_key] == search_value), None)
        return result_dict

    def get_control_parameter_label_by_id(self, control, param_id):
        """Return value of a parameter of a control by id of parameter"""
        param = self.find_dict_by_value(control['parameters'], "id", param_id)
        return param['label']

    def get_control_prose_as_markdown(self, control_data, part_types={ "statement" }):
        # Concatenate the prose text of all of the 'parts' of this control
        # in Markdown. Filter out the parts that are not wanted.
        # Example 'statement'
        #   python3 -c "import oscal; cg = oscal.Catalog(); print(cg.get_control_prose_as_markdown(cg.get_control_by_id('ac-6')))"
        # Example 'guidance'
        #   python3 -c "import oscal; cg = oscal.Catalog(); print(cg.get_control_prose_as_markdown(cg.get_control_by_id('ac-6'), part_types={'guidance'}))"

        return self.format_part_as_markdown(control_data, filter_name=part_types)

    def format_part_as_markdown(self, part, indentation_level=-1, indentation_string="    ", filter_name=None, hide_first_label=True):
        # Format part, which is either a control or a part, as Markdown.

        # First construct the prose text of this part. If there is a
        # label, put it at the start.

        md = ""

        # If this part has a label (i.e. "a."), get the label.
        label = ""
        label_property = self.find_dict_by_value(part.get('properties', []), 'name', 'label')
        if label_property:
            label = label_property['value'] + " "
        # Hide first label to avoid showing control_id
        if indentation_level == -1 and hide_first_label:
            label = ""
        # Emit the label, if any.
        md += label

        # If it has a 'prose' key, then add that. The 'prose' is a string
        # that may contain Markdown formatting, so we don't touch it much
        # because we are supposed to produce markdown.
        #
        # OSCAL defines "markup-multiline" to use two escaped \n's to
        # denote paragraph boundaries, so we replace the literal "\n\n"
        # with two actual newline characters.
        if 'prose' in part:
            prose = part['prose']
            prose = prose.replace("\\n\\n", "\n\n")
            md += prose

        # If prose is multiple lines and if there is a label, then to be
        # valid Markdown, all lines after the first should be indented
        # the number of characters in the label (plus its space).
        if label:
            md = md.split("\n")
            for i in range(1, len(md)):
                md[i] = (" " * len(label)) + md[i]
            md = "\n".join(md)

        # Apply indentation. Each line of the prose should be indented
        # (not just the first line). Break the prose up into lines,
        # add the indentation at the start of each line, and then put
        # the lines back together again.
        # In Python, a string times an integer repeats it.
        md = "\n".join([
            (indentation_level*indentation_string) + line
            for line in md.split("\n")
        ])

        # If there was any prose text, add a paragraph boundary.
        if md != "":
            md += "\n\n"

        # If it has sub-parts, then emit those.
        if "parts" in part:
            for part in part["parts"]:
                # If filter_name is given, filter out the parts that don't have
                # one of the givne names.
                if filter_name and part.get('name') not in filter_name:
                    continue

                # Append this part.
                md += self.format_part_as_markdown(part,
                                                   indentation_string=indentation_string,
                                                   indentation_level=indentation_level+1)

        return md

    def get_flattened_control_as_dict(self, control):
        """Return a control as a simplified, flattened Python dictionary"""
        cl_dict = {
            "id": control['id'],
            "id_display": re.sub(r'^([A-Za-z][A-Za-z]-)([0-9]*)\.([0-9]*)$',r'\1\2 (\3)', control['id']),
            "title": control['title'],
            "family_id": control['id'].split("-")[0],
            "family_title": self.get_group_title_by_id(control['id'].split("-")[0]),
            "class": control['class'],
            "description": self.get_control_prose_as_markdown(control, part_types={ "statement" }),
            "guidance": self.get_control_prose_as_markdown(control, part_types={ "guidance" }),
            "catalog_file": self.catalog_file,
            "catalog_id": self.catalog_id
        }
        # cl_dict = {"id": "te-1", "title": "Test Control"}
        return cl_dict

    def get_flattended_controls_all_as_dict(self):
        """Return all controls as a simplified flattened Python dictionary indexed by control ids"""
        # Create an empty dictionary
        cl_all_dict = {'ac-1': {}}
        # Get all the controls
        for cl in self.get_controls_all():
            # Get flattened control and add to dictionary of controls
            cl_dict = self.get_flattened_control_as_dict(cl)
            cl_all_dict[cl_dict['id']] = cl_dict
        return cl_all_dict