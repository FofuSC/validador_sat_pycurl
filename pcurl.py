import pycurl
import StringIO
from xml.dom import minidom
from os import remove
from lxml import etree

emisor = receptor = total = uuid = xml = ""
io = StringIO.StringIO()

ruta_xml = raw_input("Ruta XML: ")
file = etree.parse(ruta_xml)

emisor = file.xpath('//cfdi:Emisor/@Rfc', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/3'})
receptor = file.xpath('//cfdi:Receptor/@Rfc', namespaces={'cfdi': "http://www.sat.gob.mx/cfd/3"})
total = file.xpath('//@Total')
uuid = file.xpath('//tfd:TimbreFiscalDigital/@UUID', namespaces={'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'})
xml = "?re=" + emisor[0] + "&amp;rr=" + receptor[0] + "&amp;tt=" + total[0] + "&amp;id=" + uuid[0]

url = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc"
soap = """
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
			<soapenv:Body>
				<tem:Consulta>
					<tem:expresionImpresa>""" + str(xml) + """</tem:expresionImpresa>
				</tem:Consulta>
			</soapenv:Body>
		</soapenv:Envelope>
		""" 
headers = ['Host: consultaqr.facturaelectronica.sat.gob.mx',
       'POST: https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc HTTP/1.1',
       'SOAPAction: http://tempuri.org/IConsultaCFDIService/Consulta',
       'Content-Type: text/xml; charset=utf-8',
       'Connection: keep-Alive',
       'Content-Length: ' + str(len(soap)) ,]

c = pycurl.Curl()
c.setopt(c.URL, url)
c.setopt(c.WRITEFUNCTION, io.write)
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, soap)
c.setopt(c.HTTPHEADER, headers)
c.setopt(c.SSL_VERIFYPEER, 1)
c.setopt(c.SSL_VERIFYHOST, 2)

try:
	c.perform()
	response = io.getvalue()

	file = open("content.xml", "w")
	file.write(response)
	file.close()

	file = open("content.xml", "r")
	doc = etree.parse(file)
	print(doc.xpath('//a:CodigoEstatus/text()', namespaces={'a': 'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'}))
except pycurl.error as e:
	print(e)
finally:
	c.close()
	file.close()
	remove("content.xml")

"""
	http://pycurl.io/docs/latest/curlobject.html
	https://stackoverflow.com/questions/43424677/http-error-411-the-request-must-be-chunked-or-have-a-content-length
	https://stackoverflow.com/questions/8332643/pycurl-and-ssl-cert
	https://stackoverflow.com/questions/872844/pycurl-returntransfer-option-doesnt-exist
	https://developers.sw.com.mx/knowledge-base/servicio-publico-de-consulta-estatus-cfdi-sat/
	https://tar.mx/archivo/2018/validar-folio-fiscal-cfdi-con-php-directo-del-sat-2018.html
	https://es.stackoverflow.com/questions/182229/problema-para-extraer-atributo-con-un-valor-espec%C3%ADfico-de-un-xml-usando-python
	https://lxml.de/xpathxslt.html#the-xpath-method
	https://docs.python.org/3/library/xml.etree.elementtree.html
	https://stackoverflow.com/questions/24038744/namespace-error-lxml-xpath-python
"""