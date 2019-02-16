from io import BytesIO
import logging
from os import path

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class PDFGenerator(object):
    """
    A class containing all the methods for populating a NationalGrid contract
    """
    
    INPUT_FILENAME = 'nationalgrid_schedule_z.pdf'
    
    def __init__(self):
        super(PDFGenerator, self).__init__()
        
        # A list of pages to add (i.e. merge) to the original PDF found in INPUT_FILENAME.
        # Each element of the list is a tuple (iterable-or-None, PDFFileReader). The
        # PDFFileReader is a one-page PDF to be merged with the original. The iterable
        # yields all the of page numbers to merge the PDF with; if it is None, the PDF
        # will be merged with every page of the original.
        # These are zero-indexed, so if the iterable is e.g. [1], the PDF will be merged
        # with the second page.
        self.pages_to_add = []

    def add_initials(self, initials):
        """
        Makes a page with initials in the bottom right corner to be added to every
        page of the final PDF.
        """
        
        # Create a one-page PDF with initials in the bottom right corner
        packet = BytesIO()
        logging.info('Creating Initials PDF')
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(552, 32, initials)
        can.save()
        
        # Move to the beginning of the BytesIO
        packet.seek(0)
        # Create a PDF from the BytesIO
        new_pdf = PdfFileReader(packet)
        
        # Add the newly created PDF to the list of pages to merge. It will be merged with
        # every page, because the initials need to be on every page.
        self.pages_to_add.append((None, new_pdf))
    
    def add_seller_signature(self, host_name, current_date):
        """
        Makes a page with host_name and current_date to be added to the final PDF.
        """

        # Create a one-page PDF with host_name twice and current_date once
        packet = BytesIO()
        logging.info('Creating Host Data PDF')
        can = canvas.Canvas(packet, pagesize=letter)
    
        logging.info('Drawing Host Data on PDF')
        # TODO: Add box and e-signature marking around this
        can.drawString(65, 485, host_name)
        can.drawString(65, 435, host_name)
        can.drawString(65, 386, current_date)
        can.save()
        
        # Move to the beginning of the BytesIO
        packet.seek(0)
        # Create a PDF from the BytesIO
        new_pdf = PdfFileReader(packet)
        
        # Add the newly created PDF to the list of pages to merge. It will be merged with
        # the last (fourth) page only.
        self.pages_to_add.append(([3], new_pdf))
    
    def add_seller_allocation(self, percent_allocation):
        """
        Makes a page with percent_allocation to be added to the final PDF.
        """

        # Create a one-page PDF with percent_allocation
        packet = BytesIO()
        logging.info('Creating Host Data PDF')
        can = canvas.Canvas(packet, pagesize=letter)
        logging.info('Drawing Host Data on PDF')
        can.drawString(41, 89, percent_allocation)
        can.save()
        
        # Move to the beginning of the BytesIO
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        
        # Add the newly created PDF to the list of pages to merge. It will be merged with
        # the second page only.
        self.pages_to_add.append(([1], new_pdf))
    
    def add_seller_info(self, host_name, host_telephone_number, host_address, host_account_number):
        """
        Makes a page with various strings to be added to the final PDF.
        """

        # Create a one-page PDF with the inputs displayed
        packet = BytesIO()
        logging.info('Creating Host Data PDF')
        can = canvas.Canvas(packet, pagesize=letter)
        logging.info('Drawing Host Data on PDF')
        can.drawString(152, 700, host_name)
        can.drawString(400, 700, host_telephone_number)
        can.drawString(152, 676, host_address)
        can.drawString(167, 655, host_account_number)
        can.save()
        
        # Move to the beginning of the BytesIO
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        
        # Add the newly created PDF to the list of pages to merge. It will be merged with
        # the first page only.
        self.pages_to_add.append(([0], new_pdf))
    
    def add_buyer_info(self, customer_name, customer_address,
                       customer_account_number, customer_percent_allocation):
        """
        Makes a page with various strings to be added to the final PDF.
        """

        # Create a one-page PDF with the inputs displayed
        packet = BytesIO()
        logging.info('Creating Host Data PDF')
        can = canvas.Canvas(packet, pagesize=letter)
        logging.info('Drawing Host Data on PDF')
        can.drawString(145, 651, customer_name)
        can.drawString(145, 635, customer_address)
        can.drawString(175, 619, customer_account_number)
        can.drawString(273, 585, customer_percent_allocation)
        can.save()
        
        # Move to the beginning of the BytesIO
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        
        # Add the newly created PDF to the list of pages to merge. It will be merged with
        # the third page only.
        self.pages_to_add.append(([2], new_pdf))
    
    def add_all_to_pdf(self, input_folder, output_path):
        """
        Add all the PDFs in self.pages_to_add to the PDF contained in input_file_path
        :param input_folder: The folder containing the input PDF. The file that will
        be used is os.path.join(input_folder, self.INPUT_FILENAME).
        :param output_path: The file to save the final PDF to.
        """
        
        # Load the initial PDF
        input_file_path = path.join(input_folder, self.INPUT_FILENAME)
        input_pdf = PdfFileReader(input_file_path)
        
        # Create a list of PDFs to add to each page in the input PDF. This starts off as
        # a list of empty lists, because there are no pages to add yet.
        # Example value of pages_to_add and what the resulting page_pdf_list is:
        # input_pdf.getNumPages() = 3
        # self.pages_to_add = [([0], pdf1), ([0, 1], pdf2)]
        # page_pdf_list = [[pdf1, pdf2], [pdf2], []]
        page_pdf_list = [[] for _ in range(input_pdf.getNumPages())]
        for page_set, pdf in self.pages_to_add:
            # For each PDF in self.pages_to_add, add it to the pages that it will be merged with
            if page_set is None:
                # None means that the PDF is added to each page
                for page in range(input_pdf.getNumPages()):
                    page_pdf_list[page].append(pdf)
            else:
                for page in page_set:
                    page_pdf_list[page].append(pdf)
        
        # Combine the input PDF with the other PDFs
        output = PdfFileWriter()
        logging.info('Merging Initials with each page of Schedule Z')
        for i in range(input_pdf.getNumPages()):
            page = input_pdf.getPage(i)
            for pdf in page_pdf_list[i]:
                # Merge each one-page PDF with this page
                page.mergePage(pdf.getPage(0))
            # Write the new page to the output
            output.addPage(page)
        
        # Write output to file
        logging.info('Writing merged output to file')
        with open(output_path, 'wb') as fn:
            output.write(fn)
