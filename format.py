import os
import sys
import subprocess
import glob


class BookMaker():
    def __init__(self, file_path=None, fake=False):
        self.fake = fake
        if file_path:
            pass # For PDF parsing
        else:
            self.file_paths = sorted(glob.glob('initial_images/*.png'), key=self.parse_page_number)
            first_file_name = os.path.split(self.file_paths[0])[-1]
            self.book_name = "".join(first_file_name.split('-')[:-1])
            print "Working with book %s" % self.book_name
            self.pages_name = "pages/%s" % self.book_name
        
    def convert_two_page_images_to_pages(self):
        """
        Sometimes we want to convert existing images (that have maybe already 
        been converted from a pdf in some other way) in to pages (IE, cut in 
        half and cropped.).
        """
        [os.remove(p) for p in glob.glob("pages/*")]
        
        for i, filename in enumerate(self.file_paths):
            args = [
                'convert', 
                '-crop',
                '50%x100%',
                '-trim',
                '+repage',
                '%s' % filename,
                "%s-%s.png" % (self.pages_name, i)]
        
            # if not self.fake: subprocess.call(" ".join(args), shell=True)
            subprocess.call(" ".join(args), shell=True)
        # sys.exit()
        self.rename_pages()
        self.populate_pages()
        self.group_pages()
    
    def rename_pages(self):
        def sort_pages(key):
            if len(key.split('-')) == 3:
                a,b = key.split('-')[1:3]
                b = b.split('.')[0]
                a, b = map(int, (a,b))
                n = a*2
                if b == 1:
                    n = n + 1            
                return n, key
            else:
                return key.split('-')[-1].split('.')[0], key
            
        page_files = glob.glob("%s*" % self.pages_name)
        numbered_pages = [sort_pages(f) for f in page_files]
        self.pages = [b for a,b in sorted(numbered_pages)]
        for i, f in enumerate(self.pages):
            os.rename(f, "pages/%s-%s.png" % (self.book_name, i))
        self.pages = sorted(glob.glob("%s*" % self.pages_name), key=self.parse_page_number)
        
    def parse_page_number(self, key):
        n = int(key.split('-')[-1].split('.')[0])
        return n
    
    def convert_pages_from_pdf(self):
        return ""
        # args = [
        #     'convert', 
        #     '-density',
        #     '200',
        #     '-crop',
        #     '50%x100%',
        #     '-trim',
        #     '+repage',
        #     '%s' % self.file_path,
        #     "%s.png" % self.out_file_name]
        # 
        # subprocess.call(" ".join(args), shell=True)
        # self.populate_pages()
    
    def populate_pages(self):
        self.pages.insert(0, 'blank.png')
        
        self.num_pages = len(self.pages)
        self.group_pages()
        
    
    def group_pages(self, n=8):
        """
        Group pages in to groups of n
        """
        
        i = 0
        self.page_groups = []
        group = []
        print self.pages
        for page in self.pages:
            if len(group) == n:
                self.page_groups.append(group)
                group = []
            group.append(page)
        
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
        page = 0
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
                    
            reordered_page_groups = zip(*[reordered[i::4] for i in range(4)])
            # reordered_page_groups = reordered
            # print reordered

            for x, g in enumerate(reordered_page_groups):
                print x
                print g
                args = [
                    'montage',
                    " ".join(g),
                    '-tile',
                    '2x2',
                    '-geometry',
                    '+0+0',
                    'books/%s-%s-%s.png' % (self.book_name, i, page)
                ]
                page = page + 1
                # montage ordered* -tile 2x2 -geometry +0+0 montage.jpg
                subprocess.call(" ".join(args), shell=True)


if __name__ == "__main__":
    if 'image' in sys.argv:
        # We're working with a set of images
        # Basic flow:
        #   1. Split all image in initial_images in half, and store them in pages
        #   2. Grab the page number of all these images and order them
        #   3. Pass this list of pages to format_2_fold, and get it to store it 
        #      in the books folder
        book = BookMaker(fake=False)
        book.convert_two_page_images_to_pages()
        book.format_2_fold()
        
        pass
    elif 'pdf' in sys.argv:
        # We're working with a PDF
        raise NotImplementedError("I've not done this yet")
    else:
        print """
    format.py [image|pdf]
    Converts with an image or pdf in to a 2 fold book, in 8 page 
    'blocks'.

    Usage:
        * image: convert all images in initial_images to a book
        * pdf: Convert a pdf in pdfs in to a book
            
        """
    # for pdf in glob.glob('initial_images/*.png'):
    #     book = BookMaker(pdf)
    #     book.convert_images_to_pages()
    #     book.format_2_fold()
    #     
    # # else:
    # #     for pdf in glob.glob('pdfs/*.pdf'):
    # #         book = BookMaker(pdf)
    # #         book.convert_pages_from_pdf()
    # #         book.format_2_fold()
    # 
    # 
    # 
