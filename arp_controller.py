from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import arp

log = core.getLogger()

def _handle_PacketIn(event):
    packet = event.parsed

    if not packet.parsed:
        log.warning("Ignoring incomplete packet")
        return

    arp_packet = packet.find('arp')

    # Handle ARP requests
    if arp_packet and arp_packet.opcode == arp.REQUEST:
        log.info("ARP request: %s -> %s", arp_packet.protosrc, arp_packet.protodst)

        # Flood ARP so destination host can respond
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)
        return

    # Flood all other packets (ICMP, etc.)
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Simple ARP + Flood Controller Started")