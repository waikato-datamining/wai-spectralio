from ..options import Option, OptionHandler


class ProductCodeOptionsMixin(OptionHandler):

    product_code = Option(
        help="either the attribute name with the product code in it, or the actual product code to be used",
        default="01")

    product_code_from_field = Option(
        help="whether to use the product code option as the attribute name containing the actual product code",
        action="store_true")
