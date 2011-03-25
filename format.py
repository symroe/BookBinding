import os
import sys
import subprocess
import glob


class BookMaker():
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.split(self.file_path)[1]
        self.pdf_name = os.path.split(self.file_path)[1]
        self.book_name = self.pdf_name[:-4]
        self.out_file_name = "pages/%s" % self.book_name
        
    def convert_images_to_pages(self):
        """
        Sometimes we want to convert existing images (that have maybe already 
        been converted from a pdf in some other way) in to pages (IE, cut in 
        half and cropped.).
        """
        
        args = [
            'convert', 
            '-crop',
            '50%x100%',
            '-trim',
            '+repage',
            '%s' % self.file_path,
            "%s.png" % self.out_file_name]
        
        subprocess.call(" ".join(args), shell=True)
        self.populate_pages()
        
        
    
    def convert_pages_from_pdf(self):
        args = [
            'convert', 
            '-density',
            '200',
            '-crop',
            '50%x100%',
            '-trim',
            '+repage',
            '%s' % self.file_path,
            "%s.png" % self.out_file_name]
        
        subprocess.call(" ".join(args), shell=True)
        self.populate_pages()
    
    def populate_pages(self):
        self.pages = sorted(glob.glob("%s*" % self.out_file_name), key=self.parse_page_number)
        self.pages.insert(0, 'pages/blank.png')
        
        self.num_pages = len(self.pages)
        self.group_pages()
        
    
    def group_pages(self, n=8):
        """
        Group pages in to groups of n
        """
        
        i = 0
        self.page_groups = []
        group = []
        for page in self.pages:
            if len(group) == n:
                self.page_groups.append(group)
                group = []
            group.append(page)

    def parse_page_number(self, key):
        return int(key.split('-')[-1].split('.')[0])
    
    def rotate_page(self, page):
        args = [
            'convert',
            page,
            '-rotate',
            '180',
            page
        ]
        subprocess.call(" ".join(args), shell=True)
    
    def format_2_fold(self):
        rotate = (2,3,4,5)
        order = (7,0,4,3,1,6,2,5)
        for i, group in enumerate(self.page_groups):
            for n in order:
                if n in range(len(group)):
                    if n in rotate:
                        self.rotate_page(group[n])
            reordered = []
            for j in order:
                try:
                    reordered.append(group[j])
                except KeyError:
                    break
                        
            args = [
                'montage',
                " ".join(reordered),
                '-tile',
                '2x2',
                '-geometry +0+0',
                'books/%s-%s.png' % (self.book_name, i)
            ]
            # montage ordered* -tile 2x2 -geometry +0+0 montage.jpg
            subprocess.call(" ".join(args), shell=True)


if __name__ == "__main__":
    if 'image' in sys.argv:
        for pdf in glob.glob('initial_images/*.png'):
            book = BookMaker(pdf)
            book.convert_images_to_pages()
            book.format_2_fold()
        
    else:
        for pdf in glob.glob('pdfs/*.pdf'):
            book = BookMaker(pdf)
            book.convert_pages_from_pdf()
            book.format_2_fold()



