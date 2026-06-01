import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


class PDFGenerator:
    @staticmethod
    def __remove_pl(text):
        pl_map = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
        return str(text).translate(pl_map)

    @staticmethod
    def create_rental_report(file_path, rentals, clients, vehicles):
        client_map = {str(c.get_id()): c for c in clients}
        vehicle_map = {str(v.get_id()): v for v in vehicles}

        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30,
                                bottomMargin=30)
        story = []

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        story.append(Paragraph(PDFGenerator.__remove_pl("EWIDENCJA AKTUALNYCH WYPOZYCZEN"), styles['Heading1']))
        story.append(Spacer(1, 15))

        table_data = [[
            Paragraph("Klient (Imie Nazwisko PESEL)", normal_style),
            Paragraph("Pojazd (Marka Model Tablica)", normal_style),
            Paragraph("Miejsce Zwrotu", normal_style),
            Paragraph("Termin Konca", normal_style)
        ]]

        for r in rentals:
            if isinstance(r, dict):
                c_id = str(r.get("client_id", ""))
                v_id = str(r.get("vehicle_id", ""))
                loc = r.get("location_area", "Nieokreslone")
                end_date = r.get("end_date", "Brak terminu")
            else:
                c_id = str(
                    r.get_client_id() if hasattr(r, 'get_client_id') else r.__dict__.get('_Rental__client_id', ''))
                v_id = str(
                    r.get_vehicle_id() if hasattr(r, 'get_vehicle_id') else r.__dict__.get('_Rental__vehicle_id', ''))
                loc = r.get_location_area() if hasattr(r, 'get_location_area') else r.__dict__.get(
                    '_Rental__location_area', 'Nieokreslone')
                end_date = r.get_end_date() if hasattr(r, 'get_end_date') else "Brak terminu"

            if not end_date or str(end_date).strip() == "None" or "-" not in str(end_date):
                end_date = "Brak terminu"

            c_obj = client_map.get(c_id)
            c_text = f"{c_obj.get_name()} {c_obj.get_surname()} ({c_obj.get_pesel()})" if c_obj else f"ID: {c_id}"

            v_obj = vehicle_map.get(v_id)
            v_text = f"{v_obj.get_brand()} {v_obj.get_model()} ({v_obj.get_plate()})" if v_obj else f"ID: {v_id}"

            if not loc or loc == "None": loc = "Nieokreslone"

            table_data.append([
                Paragraph(PDFGenerator.__remove_pl(c_text), normal_style),
                Paragraph(PDFGenerator.__remove_pl(v_text), normal_style),
                Paragraph(PDFGenerator.__remove_pl(loc), normal_style),
                Paragraph(PDFGenerator.__remove_pl(end_date), normal_style)
            ])

        pdf_table = Table(table_data, colWidths=[150, 150, 130, 100])
        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(pdf_table)
        doc.build(story)

    @staticmethod
    def create_map_report(file_path, rentals, clients, vehicles, temp_img_path):
        client_map = {str(c.get_id()): c for c in clients}
        vehicle_map = {str(v.get_id()): v for v in vehicles}

        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30,
                                bottomMargin=30)
        story = []

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        story.append(Paragraph(PDFGenerator.__remove_pl("EWIDENCJA LOKALIZACJI POJAZDOW (MAPA)"), styles['Heading1']))
        story.append(Spacer(1, 10))

        if temp_img_path and os.path.exists(temp_img_path):
            story.append(Image(temp_img_path, width=530, height=280))
            story.append(Spacer(1, 15))

        table_data = [[
            Paragraph("Klient", normal_style),
            Paragraph("Pojazd", normal_style),
            Paragraph("Lokalizacja (Miejsce Zwrotu)", normal_style),
            Paragraph("Termin", normal_style)
        ]]

        for r in rentals:
            if isinstance(r, dict):
                c_id = str(r.get("client_id", ""))
                v_id = str(r.get("vehicle_id", ""))
                loc = r.get("location_area", "Nieokreslone")
                end_date = r.get("end_date", "Brak terminu")
            else:
                c_id = str(
                    r.get_client_id() if hasattr(r, 'get_client_id') else r.__dict__.get('_Rental__client_id', ''))
                v_id = str(
                    r.get_vehicle_id() if hasattr(r, 'get_vehicle_id') else r.__dict__.get('_Rental__vehicle_id', ''))
                loc = r.get_location_area() if hasattr(r, 'get_location_area') else r.__dict__.get(
                    '_Rental__location_area', 'Nieokreslone')
                end_date = r.get_end_date() if hasattr(r, 'get_end_date') else "Brak terminu"

            if not end_date or str(end_date).strip() == "None" or "-" not in str(end_date):
                end_date = "Brak terminu"

            client_obj = client_map.get(c_id)
            c_text = f"{client_obj.get_name()} {client_obj.get_surname()}" if client_obj else f"ID: {c_id}"

            vehicle_obj = vehicle_map.get(v_id)
            v_text = f"{vehicle_obj.get_brand()} {vehicle_obj.get_model()}" if vehicle_obj else f"ID: {v_id}"

            if not loc or loc == "None": loc = "Nieokreslone"

            table_data.append([
                Paragraph(PDFGenerator.__remove_pl(c_text), normal_style),
                Paragraph(PDFGenerator.__remove_pl(v_text), normal_style),
                Paragraph(PDFGenerator.__remove_pl(loc), normal_style),
                Paragraph(PDFGenerator.__remove_pl(end_date), normal_style)
            ])

        pdf_table = Table(table_data, colWidths=[140, 140, 140, 110])
        pdf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(pdf_table)
        doc.build(story)
