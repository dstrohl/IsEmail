# IsEmail
Email validation tool


    is_email = IsEmail()
    response = is_email("test_email")

response object

bool(response)
* Will return True if no errors or if warnings
* Will return False if errors

response.is_error

response.is_warning

response.is_ok

response.comments
* returns iterable for all comments
* comment record =
    * comment.text = text
    * comment.start = start position
    * comment.end = end position
    * comment.responses = multiresponse_obj

response.email_in = initial email string

response.cleaned_email = email without comments

response.responses = multi-response object

response.local_part

response.domain_part

response.response_text

response.long_text

response.detailed_text


verbose
* 0 = only return true/false
* 1 = return t/f + cleaned email + major reason
* 2 = return all


Categories
**********
[100] ISEMAIL_VALID_CATEGORY  Address is valid
[107]        ISEMAIL_DNSWARN  Address is valid but a DNS check was not successful
[115]        ISEMAIL_RFC5321  Address is valid for SMTP but has unusual elements
[131]           ISEMAIL_CFWS  Address is valid within the message but cannot be used unmodified for the envelope
[500]         ISEMAIL_DEPREC  Address contains deprecated elements but may still be valid in restricted contexts
[775]        ISEMAIL_RFC5322  The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.
[999]            ISEMAIL_ERR  Address is invalid for any purpose


Diags
*********
[1000]                     VALID  Valid Email (ISEMAIL_VALID_CATEGORY)
[1005]      DNSWARN_NO_MX_RECORD  Couldn't find an MX record for this domain but an A-record does exist (ISEMAIL_DNSWARN)
[1006]         DNSWARN_NO_RECORD  Couldn't find an MX record or an A-record for this domain (ISEMAIL_DNSWARN)
[1009]               RFC5321_TLD  Address is valid but at a Top Level Domain (ISEMAIL_RFC5321)
[1010]       RFC5321_TLD_NUMERIC  Address is valid but the Top Level Domain begins with a number (ISEMAIL_RFC5321)
[1011]     RFC5321_QUOTED_STRING  Address is valid but contains a quoted string (ISEMAIL_RFC5321)
[1012]   RFC5321_ADDRESS_LITERAL  Address is valid but at a literal address not a domain (ISEMAIL_RFC5321)
[1013]   RFC5321_IPV6_DEPRECATED  Address is valid but contains a :: that only elides one zero group. All implementations must accept and be able to handle any legitimate RFC 4291 format. (ISEMAIL_DEPREC)
[1017]              CFWS_COMMENT  Address contains comments (ISEMAIL_CFWS)
[1018]                  CFWS_FWS  Address contains FWS (ISEMAIL_CFWS)
[1033]         DEPREC_LOCAL_PART  The local part is in a deprecated form (ISEMAIL_DEPREC)
[1034]                DEPREC_FWS  Address contains an obsolete form of Folding White Space (ISEMAIL_DEPREC)
[1035]              DEPREC_QTEXT  A quoted string contains a deprecated character (ISEMAIL_DEPREC)
[1036]                 DEPREC_QP  A quoted pair contains a deprecated character (ISEMAIL_DEPREC)
[1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)
[1038]              DEPREC_CTEXT  A comment contains a deprecated character (ISEMAIL_DEPREC)
[1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)
[1065]            RFC5322_DOMAIN  Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS (ISEMAIL_RFC5322)
[1066]          RFC5322_TOO_LONG  Address is too long (ISEMAIL_RFC5322)
[1067]    RFC5322_LOCAL_TOO_LONG  The local part of the address is too long (ISEMAIL_RFC5322)
[1068]   RFC5322_DOMAIN_TOO_LONG  The domain part is too long (ISEMAIL_RFC5322)
[1069]    RFC5322_LABEL_TOO_LONG  The domain part contains an element that is too long (ISEMAIL_RFC5322)
[1070]    RFC5322_DOMAIN_LITERAL  The domain literal is not a valid RFC 5321 address literal (ISEMAIL_RFC5322)
[1071] RFC5322_DOM_LIT_OBS_DTEXT  The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters (ISEMAIL_RFC5322)
[1072]    RFC5322_IPV6_GRP_COUNT  The IPv6 literal address contains the wrong number of groups (ISEMAIL_RFC5322)
[1073]   RFC5322_IPV6_2X2X_COLON  The IPv6 literal address contains too many :: sequences (ISEMAIL_RFC5322)
[1074]     RFC5322_IPV6_BAD_CHAR  The IPv6 address contains an illegal group of characters (ISEMAIL_RFC5322)
[1075]     RFC5322_IPV6_MAX_GRPS  The IPv6 address has too many groups (ISEMAIL_RFC5322)
[1076]   RFC5322_IPV6_COLON_STRT  IPv6 address starts with a single colon (ISEMAIL_RFC5322)
[1077]    RFC5322_IPV6_COLON_END  IPv6 address ends with a single colon (ISEMAIL_RFC5322)
[1129]       ERR_EXPECTING_DTEXT  A domain literal contains a character that is not allowed (ISEMAIL_ERR)
[1130]         ERR_NO_LOCAL_PART  Address has no local part (ISEMAIL_ERR)
[1131]        ERR_NO_DOMAIN_PART  Address has no domain part (ISEMAIL_ERR)
[1132]      ERR_CONSECUTIVE_DOTS  The address may not contain consecutive dots (ISEMAIL_ERR)
[1133]      ERR_ATEXT_AFTER_CFWS  Address contains text after a comment or Folding White Space (ISEMAIL_ERR)
[1134]        ERR_ATEXT_AFTER_QS  Address contains text after a quoted string (ISEMAIL_ERR)
[1135]    ERR_ATEXT_AFTER_DOMLIT  Extra characters were found after the end of the domain literal (ISEMAIL_ERR)
[1136]       ERR_EXPECTING_QPAIR  The address contains a character that is not allowed in a quoted pair (ISEMAIL_ERR)
[1137]       ERR_EXPECTING_ATEXT  Address contains a character that is not allowed (ISEMAIL_ERR)
[1138]       ERR_EXPECTING_QTEXT  A quoted string contains a character that is not allowed (ISEMAIL_ERR)
[1139]       ERR_EXPECTING_CTEXT  A comment contains a character that is not allowed (ISEMAIL_ERR)
[1140]         ERR_BACKSLASH_END  The address can't end with a backslash (ISEMAIL_ERR)
[1141]             ERR_DOT_START  Neither part of the address may begin with a dot (ISEMAIL_ERR)
[1142]               ERR_DOT_END  Neither part of the address may end with a dot (ISEMAIL_ERR)
[1143]   ERR_DOMAIN_HYPHEN_START  A domain or subdomain cannot begin with a hyphen (ISEMAIL_ERR)
[1144]     ERR_DOMAIN_HYPHEN_END  A domain or subdomain cannot end with a hyphen (ISEMAIL_ERR)
[1145]   ERR_UNCLOSED_QUOTED_STR  Unclosed quoted string (ISEMAIL_ERR)
[1146]      ERR_UNCLOSED_COMMENT  Unclosed comment (ISEMAIL_ERR)
[1147]      ERR_UNCLOSED_DOM_LIT  Domain literal is missing its closing bracket (ISEMAIL_ERR)
[1148]           ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
[1149]          ERR_FWS_CRLF_END  Folding White Space ends with a CRLF sequence (ISEMAIL_ERR)
[1150]              ERR_CR_NO_LF  Address contains a carriage return that is not followed by a line feed (ISEMAIL_ERR)
[1151]         ERR_NO_DOMAIN_SEP  Address does not contain a domain seperator (@ sign) (ISEMAIL_ERR)
[1255]         ERR_EMPTY_ADDRESS  Empty Address Passed (ISEMAIL_ERR)



Breakout String:

blah@blah.com

blah    :  local part
    blah    :  ATEXT
        blah    :  FWS
        blah    :  FWS

@       : AT
blah.com
