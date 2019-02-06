# -*- coding: utf-8 -*-
{
    'name': "Contract Management",
    'summary': "Exercise module for Odoo 8",
    'description': """
    This module is not for production purposes. It's just a sample.
    Just install it.
    
    It creates 3 users in the three following roles :
    * Worker
    * Author
    * Manager
    
    The password is the letter a (awesome security level ^^)
    
    Don't forget to :

    * Change the default email addresses specified in the demo partner's data
    * Modify the default SMTP server settings for outgoing emails or delete and replace it by explicit command line arguments.
      => Odoo 8 requires that no SMTP server has been defined for using the SMTP command line arguments.
    * Specify a valid value for the 'email_from' parameter or the server won't be able to send messages.
    
    I didn't put the demo data reference in the proper attribute 'demo' for convenience reasons.
    
    Enjoy
    
    """,
    'author': "Manu AMIEL",
    'website': "https://github.com/manu-amiel/odoo-8-contract-management",
    'category': 'Contract Management',
    'version': '0.1',
    'depends': ['base'],
    'installable': True,
    'application': True,
    'data': [
        'security/access.xml',
        'views/contract.xml',
        'views/workflow.xml',
        # Should be moved into demo attribute
        'data/demo.xml'
    ],
}
