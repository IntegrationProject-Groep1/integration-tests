import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Script to regenerate all project XSDs from validated XML fixtures.
# Usage: python integration-tests/scripts/generate_xsds.py

REPO_ROOT = Path(__file__).parent.parent.parent
FIXTURES = REPO_ROOT / "integration-tests" / "fixtures"

# Mappings: (Fixture Subdir, Fixture Name, Target XSD Path Relative to REPO_ROOT)
MAPPINGS = [
    ("frontend", "new_registration.xml", "IP-groep1-frontend/xsd/new_registration.xsd"),
    ("crm", "new_registration_to_kassa.xml", "Kassa/integratie/schemas/schema_new_registration.xsd"),
    ("frontend", "session_create_request.xml", "Planning/xsd/session_create_request.xsd"),
    ("planning", "session_created.xml", "IP-groep1-frontend/xsd/session_created.xsd"),
    ("planning", "session_created.xml", "Planning/xsd/session_created.xsd"),
    ("frontend", "session_view_request.xml", "Planning/xsd/session_view_request.xsd"),
    ("planning", "session_view_response.xml", "Planning/xsd/session_view_request.xsd"), # Note: might be response or request depending on test
    ("planning", "session_view_response.xml", "Planning/xsd/session_view_response.xsd"),
    ("planning", "session_view_response.xml", "IP-groep1-frontend/xsd/session_view_response.xsd"),
    ("planning", "session_updated.xml", "IP-groep1-frontend/xsd/session_updated.xsd"),
    ("frontend", "session_delete_request.xml", "Planning/xsd/session_delete_request.xsd"),
    ("planning", "session_deleted.xml", "IP-groep1-frontend/xsd/session_deleted.xsd"),
    ("frontend", "calendar_invite.xml", "Planning/xsd/calendar_invite.xsd"),
    ("frontend", "calendar_invite.xml", "IP-groep1-frontend/xsd/calendar_invite.xsd"),
    ("planning", "calendar_invite_confirmed.xml", "IP-groep1-frontend/xsd/calendar_invite_confirmed.xsd"),
    ("kassa", "payment_registered.xml", "Kassa/integratie/schemas/schema_payment_registered_v2.1.xsd"),
    ("crm", "payment_registered_to_facturatie.xml", "Facturatie/src/services/xsd/payment_registered.xsd"),
    ("kassa", "consumption_order.xml", "Kassa/integratie/schemas/schema_consumption_order_v2.3.xsd"),
    ("crm", "consumption_order_to_facturatie.xml", "Facturatie/src/services/xsd/consumption_order.xsd"),
    ("crm", "invoice_request.xml", "Facturatie/src/services/xsd/invoice_request.xsd"),
    ("facturatie", "invoice_status.xml", "Facturatie/src/services/xsd/invoice_status.xsd"),
    ("facturatie", "send_mailing.xml", "Facturatie/src/services/xsd/send_mailing.xsd"),
    ("crm", "invoice_cancelled.xml", "Facturatie/src/services/xsd/invoice_cancelled.xsd"),
    ("heartbeat", "heartbeat.xml", "heartbeat/heartbeat.xsd"),
    ("frontend", "user_created.xml", "CRM/xsd/user_created.xsd"),
    ("frontend", "user_registered.xml", "CRM/xsd/user_registered.xsd"),
    ("frontend", "user_updated.xml", "CRM/xsd/user_updated.xsd"),
    ("frontend", "user_deleted.xml", "CRM/xsd/user_deleted.xsd"),
    ("frontend", "business_invite.xml", "CRM/xsd/business_invite.xsd"),
    ("frontend", "cancel_registration.xml", "CRM/xsd/cancel_registration.xsd"),
    ("frontend", "event_ended.xml", "CRM/xsd/event_ended.xsd"),
    ("frontend", "log.xml", "monitoring/xsd/log.xsd"),
    ("kassa", "system_error.xml", "monitoring/xsd/system_error.xsd"),
    ("crm", "wallet_remote_topup.xml", "Kassa/integratie/schemas/wallet_remote_topup.xsd"),
    ("crm", "wallet_lease_grant.xml", "Kassa/integratie/schemas/wallet_lease_grant.xsd"),
    ("crm", "wallet_balance_update.xml", "IP-groep1-frontend/xsd/wallet_balance_update.xsd"),
    ("planning", "session_occupancy_update.xml", "IP-groep1-frontend/xsd/session_occupancy_update.xsd"),
    ("crm", "vat_validation_error.xml", "IP-groep1-frontend/xsd/vat_validation_error.xsd"),
    ("facturatie", "invoice_available.xml", "IP-groep1-frontend/xsd/invoice_available.xsd"),
    ("crm", "profile_update.xml", "Facturatie/src/services/xsd/profile_update.xsd"),
    ("crm", "send_mailing.xml", "Mailing/xsd/send_mailing.xsd"),
    ("monitoring", "system_alert.xml", "Mailing/xsd/system_alert.xsd"),
]

def xml_to_xsd_elements(element, indent="      "):
    xsd_lines = []
    for child in element:
        name = child.tag
        if len(child) > 0:
            xsd_lines.append(f'{indent}<xs:element name="{name}">')
            xsd_lines.append(f'{indent}  <xs:complexType>')
            xsd_lines.append(f'{indent}    <xs:sequence>')
            xsd_lines.extend(xml_to_xsd_elements(child, indent + "      "))
            xsd_lines.append(f'{indent}    </xs:sequence>')
            xsd_lines.append(f'{indent}  </xs:complexType>')
            xsd_lines.append(f'{indent}</xs:element>')
        else:
            xtype = "xs:string"
            uuid_fields = ["identity_uuid", "master_uuid", "user_id", "session_id", "message_id", "correlation_id", "event_id", "company_id", "inviter_uuid", "business_id", "customer_id", "lease_id"]
            if name in uuid_fields: xtype = "UUIDType"
            elif name == "timestamp": xtype = "xs:dateTime"
            elif name == "is_company_linked": xtype = "xs:boolean"
            elif name == "date_of_birth": xtype = "xs:date"
            
            if child.attrib:
                xsd_lines.append(f'{indent}<xs:element name="{name}">')
                xsd_lines.append(f'{indent}  <xs:complexType>')
                xsd_lines.append(f'{indent}    <xs:simpleContent>')
                xsd_lines.append(f'{indent}      <xs:extension base="{xtype}">')
                for attr in child.attrib:
                    xsd_lines.append(f'{indent}        <xs:attribute name="{attr}" type="xs:string"/>')
                xsd_lines.append(f'{indent}      </xs:extension>')
                xsd_lines.append(f'{indent}    </xs:simpleContent>')
                xsd_lines.append(f'{indent}  </xs:complexType>')
                xsd_lines.append(f'{indent}</xs:element>')
            else:
                xsd_lines.append(f'{indent}<xs:element name="{name}" type="{xtype}"/>')
    return xsd_lines

def generate_xsd_from_xml(xml_path, xsd_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        event_name = root.find('.//header/type').text if root.find('.//header/type') is not None else os.path.basename(xml_path).replace('.xml', '')
        source_val = root.find('.//header/source').text if root.find('.//header/source') is not None else "unknown"
        
        body = root.find('body')
        if body is None: return
        
        body_elements = xml_to_xsd_elements(body, "            ")
        body_xml = "\n".join(body_elements)

        root_elements = set(["message", event_name, root.tag])
        root_declarations = "\n".join([f'  <xs:element name="{name}" type="MessageType"/>' for name in root_elements])

        xsd_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <xs:simpleType name="UUIDType">
    <xs:restriction base="xs:string">
      <xs:pattern value="[0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{12}}"/>
    </xs:restriction>
  </xs:simpleType>

{root_declarations}

  <xs:complexType name="MessageType">
    <xs:sequence>
      <xs:element name="header">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="message_id"     type="UUIDType"/>
            <xs:element name="timestamp"      type="xs:dateTime"/>
            <xs:element name="source">
              <xs:simpleType>
                <xs:restriction base="xs:string">
                  <xs:enumeration value="frontend"/><xs:enumeration value="Frontend"/>
                  <xs:enumeration value="crm"/><xs:enumeration value="CRM"/>
                  <xs:enumeration value="planning"/><xs:enumeration value="Planning"/>
                  <xs:enumeration value="kassa"/><xs:enumeration value="Kassa"/>
                  <xs:enumeration value="facturatie"/><xs:enumeration value="Facturatie"/>
                  <xs:enumeration value="monitoring"/><xs:enumeration value="Monitoring"/>
                  <xs:enumeration value="heartbeat"/><xs:enumeration value="Heartbeat"/>
                  <xs:enumeration value="unknown"/>
                </xs:restriction>
              </xs:simpleType>
            </xs:element>
            <xs:element name="type"><xs:simpleType><xs:restriction base="xs:string"><xs:enumeration value="{event_name}"/></xs:restriction></xs:simpleType></xs:element>
            <xs:element name="version"><xs:simpleType><xs:restriction base="xs:string"><xs:enumeration value="2.0"/></xs:restriction></xs:simpleType></xs:element>
            <xs:element name="correlation_id" type="UUIDType" minOccurs="0"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="body">
        <xs:complexType>
          <xs:sequence>
{body_xml}
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
  </xs:complexType>
</xs:schema>
"""
        xsd_path.parent.mkdir(parents=True, exist_ok=True)
        xsd_path.write_text(xsd_content, encoding='utf-8')
        print(f"Generated {xsd_path.relative_to(REPO_ROOT)} from {xml_path.name}")
    except Exception as e:
        print(f"Failed to process {xml_path}: {e}")

if __name__ == "__main__":
    for subdir, xml_name, rel_xsd_path in MAPPINGS:
        xml_path = FIXTURES / subdir / xml_name
        xsd_path = REPO_ROOT / rel_xsd_path
        if xml_path.exists():
            generate_xsd_from_xml(xml_path, xsd_path)
        else:
            print(f"Fixture not found: {xml_path}")
