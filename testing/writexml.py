from xml.etree import ElementTree as ET

lang = ET.parse('test.xml')

languages = lang.getroot()
type(languages)
list_languages = languages.getchildren()
type(list_languages)
list_languages
python = list_languages[0]
python.tag
python.attrib

python_properties = python.find('Properties')
python_properties.attrib['typing'] = 'duck'

projects = ET.Element('Projects')
django = ET.Element('Django', type='Web Framework')
projects.append(django)
python.append(projects)

c = ET.Element('C')
c.attrib['cross-platform'] = 'yes'
c.attrib['typing'] = 'static'
languages.append(c)

lang.write('test.xml')
