# -*- coding: utf-8 -*-
'''
    DjVu Shape Tools  
    Copyright (C) 2012 Piotr Sikora

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from djvusmooth.i18n import _
def i18n(string):
    return _(string)


menu = { 'Data' : '&Dane',
        #'View' : _('&View'),
        'View' : '&Widok',
        'hOCR' : '&hOCR',
        'File' : '&Plik',
        'Help' : 'P&omoc',
        'Edit' : '&Edytuj'
        }

app_data =  {'Author' : u'Piotr Sikora',
             'License' : u'GPL-3',
             'Website' : u'https://bitbucket.org/piotr_sikora/moredjvushapetools/',
             'Notes': u'The ideas behind this application were developed by Janusz S. Bień.\n' \
             'The work has been supported by the Ministry of Science and Higher Education\'s ' \
             'grant no. N N519 384036 (cf. https://bitbucket.org/jsbien/ndt).'
            }


menuitems = { 'ChooseDocument': [u'Wybierz &Dokument', u'Wyświetla okno wyboru dokumentu z bazy'],
                'LoadHOCR': [u'Otwórz pliki z &hOCR', u'Wyświetla okno wybór plików zawierających dane hOCR'],
                'SaveHOCR': [u'Zapisz pliki z &hOCR', u'Zapisuje zmiany w hOCR do plików'],
                'Quit': [u'&Wyjście', u'Wyjdź z programu'],
                'NextLine': [u'Następny wiersz \tCtrl+Alt+N', u'Przejdź do następnego wiersza'],
                'PrevLine': [u'Poprzedni wiersz \tCtrl+Alt+P', u'Przejdź do poprzedniego wiersza'],
                'NextChar': [u'Następny kształt \tCtrl+Shift+N', u'Przejdź do następnego kształtu bez zatwierdzenia etykiety'],
                'PrevChar': [u'Poprzedni kształt \tCtrl+P', u'Przejdź do poprzedniego kształtu bez zatwierdzenia etykiety'],
                'PrevCharToLabel': ['Poprzedni niezaetykietowany kształt \tCtrl+W', u'Przejdź do poprzedniego niezaetykietowanego kształtu bez zatwierdzenia etykiety'],
                'NextCharCommit': ['Zatwierdź etykietę \tCtrl+N', u'Przejdź do następnego kształtu, zatwierdzając etykietę dla obecnego'],
                'NextCharToLabel': ['Następny niezaetykietowany kształt \tCtrl+Shift+E',
                                    'Przejdź do następnego niezaetykietowanego kształtu bez zatwierdzania etykiety'],
                'NextCharToLabelCommit': ['Zatwierdź etykietę 2 \tCtrl+E', 'Przejdź do następnego kształtu, zatwierdzając etykietę dla obecnego'],
                'EditHierarchy': ['Edytuj hierarchię kształtów\tCtrl+O', 'Wyświetl okno pozwalające wybrać i usunąć kształt z aktualnej hierarchii'],
                'KeyboardShortcuts': ['&Skróty klawiaturowe\tF1', 'Lista skrótów klawiaturowych'],
                'About' : [_('&About'), _('More information about this program')]
                }
