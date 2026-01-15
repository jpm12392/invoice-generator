import streamlit as st
import pandas as pd
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib import colors


def generate_invoice_pdf(
    filename,
    company_name,
    company_address,
    client_name,
    client_address,
    invoice_no,
    invoice_date,
    items,
    tax_rate
):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # ------------------ Custom Styles ------------------
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#2C3E50")
    )

    right_style = ParagraphStyle(
        "RightStyle",
        parent=styles["Normal"],
        alignment=TA_RIGHT
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.grey
    )

    # ------------------ Header ------------------
    elements.append(Paragraph(company_name, title_style))
    elements.append(Paragraph(company_address, header_style))
    elements.append(Spacer(1, 20))

    header_table = Table(
        [
            [
                Paragraph(
                    f"<b>Invoice No:</b> {invoice_no}<br/>"
                    f"<b>Date:</b> {invoice_date}",
                    styles["Normal"]
                ),
                Paragraph(
                    "<b>INVOICE</b>",
                    ParagraphStyle(
                        "InvoiceLabel",
                        fontSize=18,
                        textColor=colors.HexColor("#34495E"),
                        alignment=TA_RIGHT
                    )
                )
            ]
        ],
        colWidths=[350, 150]
    )

    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # ------------------ Client Info ------------------
    client_table = Table(
        [
            [
                Paragraph("<b>Bill To</b>", styles["Normal"]),
                ""
            ],
            [
                Paragraph(client_name, styles["Normal"]),
                ""
            ],
            [
                Paragraph(client_address, styles["Normal"]),
                ""
            ]
        ],
        colWidths=[500, 0]
    )

    elements.append(client_table)
    elements.append(Spacer(1, 20))

    # ------------------ Items Table ------------------
    table_data = [["Item Description", "Qty", "Rate", "Amount"]]
    subtotal = 0

    for item in items:
        table_data.append([
            item["Item"],
            str(item["Quantity"]),
            f"Rs. {item['Price']:.2f}",
            f"Rs. {item['Total']:.2f}"
        ])
        subtotal += item["Total"]

    tax_amount = subtotal * tax_rate / 100
    grand_total = subtotal + tax_amount

    items_table = Table(
        table_data,
        colWidths=[240, 60, 80, 80]
    )

    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
    ]))

    elements.append(items_table)
    elements.append(Spacer(1, 20))

    # ------------------ Totals ------------------
    totals_table = Table(
        [
            ["Subtotal", f"Rs. {subtotal:.2f}"],
            [f"Tax ({tax_rate}%)", f"Rs. {tax_amount:.2f}"],
            ["Grand Total", f"Rs. {grand_total:.2f}"],
        ],
        colWidths=[400, 120]
    )

    totals_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(totals_table)
    elements.append(Spacer(1, 30))

    # ------------------ Footer ------------------
    elements.append(
        Paragraph(
            "Thank you for your business!",
            ParagraphStyle(
                "Footer",
                fontSize=11,
                textColor=colors.grey,
                alignment=TA_RIGHT
            )
        )
    )

    doc.build(elements)





# ------------------ Page Config ------------------
st.set_page_config(
    page_title="Invoice Generator",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Invoice Generator")

# ------------------ Session State Init ------------------
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

# ------------------ Company Details ------------------
st.subheader("🏢 Company Details")
c1, c2 = st.columns(2)

with c1:
    company_name = st.text_input("Company Name", "Tewsm Pvt Ltd")
    company_address = st.text_area("Company Address", "Bangalore, India")

with c2:
    invoice_no = st.text_input("Invoice Number", "INV-001")
    invoice_date = st.date_input("Invoice Date", date.today())

# ------------------ Client Details ------------------
st.subheader("👤 Client Details")
c3, c4 = st.columns(2)

with c3:
    client_name = st.text_input("Client Name", "Client Company")
with c4:
    client_address = st.text_area("Client Address", "Client Address")

# ------------------ Add Item ------------------
st.subheader("📦 Add Invoice Item")

i1, i2, i3, i4 = st.columns(4)

with i1:
    item_name = st.text_input("Item / Service")
with i2:
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
with i3:
    price = st.number_input("Unit Price (₹)", min_value=0.0, value=0.0, step=0.5)
with i4:
    if st.button("➕ Add Item"):
        if item_name.strip():
            st.session_state.invoice_items.append({
                "Item": item_name.strip(),
                "Quantity": int(quantity),
                "Price": float(price),
                "Total": float(quantity * price)
            })
            st.success("Item added")
        else:
            st.warning("Item name cannot be empty")

# ------------------ Items Table ------------------
st.subheader("📋 Invoice Items")

if len(st.session_state.invoice_items) > 0:
    df = pd.DataFrame.from_records(st.session_state.invoice_items)
    st.dataframe(df, use_container_width=True)

    subtotal = df["Total"].sum()
    tax_rate = st.slider("Tax (%)", 0, 30, 18)
    tax_amount = subtotal * tax_rate / 100
    grand_total = subtotal + tax_amount

    st.subheader("💰 Invoice Summary")
    s1, s2, s3 = st.columns(3)
    s1.metric("Subtotal", f"₹ {subtotal:,.2f}")
    s2.metric("Tax", f"₹ {tax_amount:,.2f}")
    s3.metric("Grand Total", f"₹ {grand_total:,.2f}")

else:
    st.info("No items added yet.")

# ------------------ Actions ------------------
st.markdown("---")
b1, b2 = st.columns(2)

with b1:
    if st.button("🧹 Clear Invoice"):
        st.session_state.invoice_items.clear()
        st.rerun()

with b2:
    if st.button("✅ Generate Invoice"):
        if len(st.session_state.invoice_items) == 0:
            st.warning("Add at least one item to generate invoice.")
        else:
            pdf_file = f"invoice_{invoice_no}.pdf"

            generate_invoice_pdf(
                filename=pdf_file,
                company_name=company_name,
                company_address=company_address,
                client_name=client_name,
                client_address=client_address,
                invoice_no=invoice_no,
                invoice_date=str(invoice_date),
                items=st.session_state.invoice_items,
                tax_rate=tax_rate
            )

            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📄 Download Invoice PDF",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

            st.success("Invoice PDF generated successfully!")

# ------------------ Footer ------------------
st.markdown("---")
st.caption("Invoice Generator • Built with Streamlit 🚀")
