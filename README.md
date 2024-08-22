# My fast pdf

## Generate and automatically layout pdf from images.

### Requirement

`PIL`

### Usage

#### 1. Import and initialize.

    from PIL import Image
    from fast_pdf import PDFGenerator, PDFFormatter

    specify_font = 'Arial.ttf'
    pdf_format = PDFFormatter.get_default_format(specify_font)
    pdf_generator = PDFGenerator.setup_from_FormatSaver(pdf_format)

#### 2. Build a page

Use ***pdf_generator.fast_build_page()*** to build page quickly.

    PDFGenerator.fast_build_page(element_list, title: str = None, description: str = None,
                    resize: (int, int) = None, specify_format: PDFFormatter = None) -> Page:

##### Arguments:

**element_list**: contains each plots' elements, a list of tuples. Title and description in the plot could be None.
`Type: list[(Image.Image or path_to_image, title, description), ...]`

**title**: the title of the page. Could be None. `Type: str`

**description**: the description of the page. Could be None. `Type: str`

**specify_format**: the format of the page. If this value is None, the page woulduse the format when setup_from_FormatSaver()
`Type: fast_pdf.PDFFormatter`

**resize**: whether to resize the plot's image to a specific size.
`Type: Tuple[int, int]`

**return**: `fast_pdf.Page`

##### Example

    test_image = Image.new('RGB', (500, 500), color=(255, 255, 255))
    test_title = 'Test title'
    test_description = 'Test description'
    test_element_list = [(test_image, test_title, test_description),
                         (test_image, test_title, None),
                         (test_image, None, test_description)]
    test_page = pdf_generator.fast_build_page(test_element_list, title=test_title, description=test_description, resize=None)

#### 3. Add a page to pdf

    pdf_generator.add_page(test_page)

#### 4. Save the pdf

    pdf_generator.save(filename)
