import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


class PDFGenerator:
    @staticmethod
    def __remove_pl(text):
        pl_map = str.maketrans("ąęćłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
        return str(text).translate(pl_map)

    @staticmethod
    def create_rental_report(file_path, rentals, clients, vehicles):
        client_map = {str(c.get_id()): c for c in clients}
        vehicle_map = {str(v.get_id()): v for v in vehicles}

        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
        story = []

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        story.append(Paragraph(PDFGenerator.__remove_pl("SZCZEGOLOWA EWIDENCJA AKTUALNYCH WYPOZYCZEN"), styles['Heading1']))
        story.append(Spacer(1, 15))

        table_data = [[
            Paragraph("<b>Klient</b>", normal_style),
            Paragraph("<b>PESEL / Kraj</b>", normal_style),
            Paragraph("<b>Pojazd (VIN)</b>", normal_style),
            Paragraph("<b>Tablica / Przebieg</b>", normal_style),
            Paragraph("<b>Strefa Zwrotu</b>", normal_style),
            Paragraph("<b>Promien</b>", normal_style),
            Paragraph("<b>Termin</b>", normal_style)
        ]]

        today = datetime.now().date()
        custom_table_styles = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]

        for idx, r in enumerate(rentals, start=1):
            c_id = str(r.get_client_id())
            v_id = str(r.get_vehicle_id())
            loc = r.get_location_area()
            end_date = r.get_end_date()
            rng = r.get_range_area()

            try:
                rental_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                if rental_date < today:
                    custom_table_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.Color(1, 0.8, 0.8)))
            except Exception:
                pass

            c_obj = client_map.get(c_id)
            c_info = f"{c_obj.get_name()} {c_obj.get_surname()}" if c_obj else f"ID: {c_id}"
            c_meta = f"{c_obj.get_pesel()}<br/>({c_obj.get_country()})" if c_obj else "---"

            v_obj = vehicle_map.get(v_id)
            v_info = f"{v_obj.get_brand()} {v_obj.get_model()}<br/>{v_obj.get_vin()}" if v_obj else f"ID: {v_id}"
            v_meta = f"{v_obj.get_plate()}<br/>{v_obj.get_mileage()} km" if v_obj else "---"

            table_data.append([
                Paragraph(PDFGenerator.__remove_pl(c_info), normal_style),
                Paragraph(PDFGenerator.__remove_pl(c_meta), normal_style),
                Paragraph(PDFGenerator.__remove_pl(v_info), normal_style),
                Paragraph(PDFGenerator.__remove_pl(v_meta), normal_style),
                Paragraph(PDFGenerator.__remove_pl(loc), normal_style),
                Paragraph(PDFGenerator.__remove_pl(f"{rng} km"), normal_style),
                Paragraph(PDFGenerator.__remove_pl(end_date), normal_style)
            ])

        pdf_table = Table(table_data, colWidths=[95, 85, 115, 85, 72, 50, 70])
        pdf_table.setStyle(TableStyle(custom_table_styles))
        story.append(pdf_table)

        story.append(Spacer(1, 20))
        legend_data = [[
            Paragraph("", normal_style),
            Paragraph("<b>Legenda:</b> Czerwone podswietlenie oznacza przekroczenie planowanego terminu zwrotu pojazdu.", normal_style)
        ]]
        legend_table = Table(legend_data, colWidths=[20, 450])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.Color(1, 0.8, 0.8)),
            ('GRID', (0, 0), (0, 0), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(legend_table)

        doc.build(story)

    @staticmethod
    def create_map_report(file_path, rentals, clients, vehicles, temp_img_path):
        client_map = {str(c.get_id()): c for c in clients}
        vehicle_map = {str(v.get_id()): v for v in vehicles}

        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
        story = []

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        story.append(Paragraph(PDFGenerator.__remove_pl("RAPORT LOKALIZACJI FLOTY ORAZ DANYCH WYPOZYCZEN"), styles['Heading1']))
        story.append(Spacer(1, 10))

        if temp_img_path and os.path.exists(temp_img_path):
            story.append(Image(temp_img_path, width=540, height=340))
            story.append(Spacer(1, 15))

        table_data = [[
            Paragraph("<b>Klient (PESEL)</b>", normal_style),
            Paragraph("<b>Pojazd (VIN)</b>", normal_style),
            Paragraph("<b>Tablica / Przebieg</b>", normal_style),
            Paragraph("<b>Miejsce / Promien</b>", normal_style),
            Paragraph("<b>Termin</b>", normal_style)
        ]]

        today = datetime.now().date()
        custom_table_styles = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]

        for idx, r in enumerate(rentals, start=1):
            c_id = str(r.get_client_id())
            v_id = str(r.get_vehicle_id())
            loc = r.get_location_area()
            end_date = r.get_end_date()
            rng = r.get_range_area()

            try:
                rental_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                if rental_date < today:
                    custom_table_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.Color(1, 0.8, 0.8)))
            except Exception:
                pass

            client_obj = client_map.get(c_id)
            c_text = f"{client_obj.get_name()} {client_obj.get_surname()}<br/>({client_obj.get_pesel()})" if client_obj else f"ID: {c_id}"

            vehicle_obj = vehicle_map.get(v_id)
            v_text = f"{vehicle_obj.get_brand()} {vehicle_obj.get_model()}<br/>{vehicle_obj.get_vin()}" if vehicle_obj else f"ID: {v_id}"
            v_meta = f"{vehicle_obj.get_plate()}<br/>{vehicle_obj.get_mileage()} km" if vehicle_obj else "---"

            table_data.append([
                Paragraph(PDFGenerator.__remove_pl(c_text), normal_style),
                Paragraph(PDFGenerator.__remove_pl(v_text), normal_style),
                Paragraph(PDFGenerator.__remove_pl(v_meta), normal_style),
                Paragraph(PDFGenerator.__remove_pl(f"{loc}<br/>(+{rng} km)"), normal_style),
                Paragraph(PDFGenerator.__remove_pl(end_date), normal_style)
            ])

        pdf_table = Table(table_data, colWidths=[120, 135, 105, 122, 90])
        pdf_table.setStyle(TableStyle(custom_table_styles))
        story.append(pdf_table)

        story.append(Spacer(1, 20))
        legend_data = [[
            Paragraph("", normal_style),
            Paragraph("<b>Legenda:</b> Czerwone podswietlenie oznacza przekroczenie planowanego terminu zwrotu pojazdu.", normal_style)
        ]]
        legend_table = Table(legend_data, colWidths=[20, 450])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.Color(1, 0.8, 0.8)),
            ('GRID', (0, 0), (0, 0), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(legend_table)

        doc.build(story)