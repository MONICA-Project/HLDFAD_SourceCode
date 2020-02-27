from shared.settings.appglobalconf import SUBSTRING_SCRAL_TOREPLACE, SELECTED_VPN_PORT


class UtilityURLConversion:
    @staticmethod
    def replace_suburl_port(sub_url_port: str, base_url: str) -> str:
        if not sub_url_port:
            return str()

        if ":" not in sub_url_port:
            return base_url

        list_elements = sub_url_port.split(":")
        list_elements[0] = base_url

        return ":".join(list_elements)

    @staticmethod
    def replace_base_url(original_complete_url: str, base_url: str) -> str:
        prefix_url = str()
        if "://" in original_complete_url:
            items = original_complete_url.split("://")
            prefix_url = items[0]
            original_complete_url = items[1]

        if "/" not in original_complete_url:
            return prefix_url+original_complete_url

        list_elements = original_complete_url.split(sep="/")

        list_elements[0] = UtilityURLConversion.replace_suburl_port(sub_url_port=list_elements[0],
                                                                    base_url=base_url)
        return prefix_url+"://"+"/".join(list_elements)

    @staticmethod
    def convert_bgwurl_to_vpnurl(input_url: str) -> str:
        vpn_tcpport_substring = ":"+str(SELECTED_VPN_PORT)
        return_url = input_url
        if vpn_tcpport_substring not in input_url and SUBSTRING_SCRAL_TOREPLACE in input_url:
            return_url = return_url.replace(SUBSTRING_SCRAL_TOREPLACE, vpn_tcpport_substring)

        return return_url
