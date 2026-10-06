# packages/ai-graph/rakshagrid/ai_graph/builder/graph_builder.py
"""
Dynamic Graph Builder for Multi-Entity Fraud Networks.

Constructs an undirected NetworkX Graph from incident and report records.
Supports Victim, Phone, UPI, BankAccount, Transaction, and Incident entity types.
Ensures entity normalization so duplicate identifiers coalesce correctly.
"""

import re
import networkx as nx
from typing import Any, Dict, List, Optional
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.ai_graph.builder")


def normalize_phone(phone: Optional[str]) -> str:
    """Normalizes phone string to standard Indian +91XXXXXXXXXX or clean digit format."""
    if not phone:
        return ""
    clean = str(phone).strip()
    digits = re.sub(r"[^\d]", "", clean)
    if not digits:
        return ""
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 11 and digits.startswith("0"):
        return f"+91{digits[1:]}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+91{digits[2:]}"
    return f"+{digits}" if clean.startswith("+") else digits


def normalize_upi(upi: Optional[str]) -> str:
    """Normalizes UPI identifier to lowercase trimmed string."""
    if not upi:
        return ""
    return str(upi).strip().lower()


def normalize_bank(bank: Optional[str]) -> str:
    """Normalizes bank account number by removing whitespace, hyphens, and leading zeros."""
    if not bank:
        return ""
    digits = re.sub(r"[\s\-]", "", str(bank).strip())
    return digits


class GraphBuilder:
    """Builds and updates NetworkX graphs from incident and fraud report datasets."""

    @staticmethod
    def build_graph(reports: List[Dict[str, Any]]) -> nx.Graph:
        """
        Dynamically constructs an undirected NetworkX graph from a list of fraud records.
        Idempotently adds nodes and edges without duplicating entities.
        """
        G = nx.Graph()

        if not reports:
            return G

        for record in reports:
            # 1. Incident Entity
            inc_id = (
                record.get("id")
                or record.get("incidentId")
                or record.get("reportId")
                or record.get("_id")
            )
            inc_node = None
            if inc_id:
                inc_node = f"incident:{str(inc_id).strip()}"
                scam_type = record.get("typeOfScam") or record.get("scamType") or "Cyber Fraud"
                amount = float(record.get("amountLost") or record.get("amount") or 0.0)
                city = record.get("city", "")
                state = record.get("state", "")
                G.add_node(
                    inc_node,
                    type="Incident",
                    label=f"Incident {inc_id} ({scam_type})",
                    incidentId=str(inc_id),
                    scamType=scam_type,
                    amount=amount,
                    city=city,
                    state=state,
                    timestamp=record.get("timestamp") or record.get("dateOfIncident", ""),
                )

            # 2. Victim Entity
            victim_id = record.get("victimId")
            victim_name = record.get("victimName") or "Anonymous Citizen"
            vic_node = None
            if victim_id or victim_name != "Anonymous Citizen":
                v_key = str(victim_id).strip() if victim_id else f"anon_{hash(victim_name) % 100000}"
                vic_node = f"victim:{v_key}"
                G.add_node(
                    vic_node,
                    type="Victim",
                    label=str(victim_name),
                    victimId=str(victim_id or v_key),
                    victimName=victim_name,
                )
                if inc_node:
                    G.add_edge(inc_node, vic_node, relation="reported_by", weight=1.0)

            # 3. Suspect Phone Entity
            raw_phone = record.get("phoneNumber") or record.get("phone") or record.get("suspectPhone")
            phone = normalize_phone(raw_phone)
            phone_node = None
            if phone:
                phone_node = f"phone:{phone}"
                G.add_node(phone_node, type="Phone", label=phone, phoneNumber=phone)
                if vic_node:
                    G.add_edge(vic_node, phone_node, relation="contacted_by", weight=1.0)
                if inc_node:
                    G.add_edge(inc_node, phone_node, relation="linked_phone", weight=1.0)

            # 4. Suspect UPI Entity
            raw_upi = record.get("upiId") or record.get("upi") or record.get("suspectUpi")
            upi = normalize_upi(raw_upi)
            upi_node = None
            if upi:
                upi_node = f"upi:{upi}"
                G.add_node(upi_node, type="UPI", label=upi, upiId=upi)
                if vic_node:
                    G.add_edge(vic_node, upi_node, relation="sent_to_upi", weight=1.0)
                if inc_node:
                    G.add_edge(inc_node, upi_node, relation="linked_upi", weight=1.0)

            # 5. Suspect Bank Account Entity
            raw_bank = record.get("bankAccount") or record.get("bank") or record.get("accountNumber")
            bank = normalize_bank(raw_bank)
            bank_node = None
            if bank:
                bank_node = f"bank:{bank}"
                G.add_node(bank_node, type="BankAccount", label=bank, bankAccount=bank)
                if vic_node:
                    G.add_edge(vic_node, bank_node, relation="transferred_to_bank", weight=1.0)
                if inc_node:
                    G.add_edge(inc_node, bank_node, relation="linked_bank", weight=1.0)

            # 6. Transaction Entity (if explicit transaction details exist)
            txn_id = record.get("transactionId") or record.get("txnId")
            amount_lost = float(record.get("amountLost") or record.get("amount") or 0.0)
            if txn_id or amount_lost > 0:
                t_key = str(txn_id).strip() if txn_id else f"txn_{inc_id or hash(f'{vic_node}_{amount_lost}') % 100000}"
                txn_node = f"transaction:{t_key}"
                G.add_node(
                    txn_node,
                    type="Transaction",
                    label=f"INR {amount_lost:,.2f}" if amount_lost > 0 else f"Txn {t_key}",
                    amount=amount_lost,
                    transactionId=t_key,
                )
                if inc_node:
                    G.add_edge(inc_node, txn_node, relation="recorded_loss", weight=1.0)
                elif vic_node:
                    G.add_edge(vic_node, txn_node, relation="made_transaction", weight=1.0)

                # Link transaction to destination payment rails
                if upi_node:
                    G.add_edge(txn_node, upi_node, relation="routed_via_upi", weight=1.0)
                if bank_node:
                    G.add_edge(txn_node, bank_node, relation="deposited_to_bank", weight=1.0)

        logger.debug(f"Constructed graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        return G


# Backward compatibility helper
build_graph_from_reports = GraphBuilder.build_graph
