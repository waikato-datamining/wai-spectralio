from ..options import Option, OptionHandler


class ProductCodeOptionsMixin(OptionHandler):
    """
    Mixin which adds options for specifying the product code
    to readers/writers.
    """
    # The literal product code or the field name reference where to find it
    product_code = Option(
        help="either the attribute name with the product code in it, or the actual product code to be used",
        default="01"
    )

    # Whether the above product_code option is the field name or literal value
    product_code_from_field = Option(
        help="whether to use the product code option as the attribute name containing the actual product code",
        action="store_true"
    )
