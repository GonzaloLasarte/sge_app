from django.test import TestCase

from gestion.models import Member

class MemberModelTests(TestCase):

    def setUp(self):
        self.member = Member.objects.create(
            number=1,
            name='Pepe',
            sirname='Perez',
            charge=Member.RESP_TITULAR,
            in_charge_of=Member.GRUPO
        )

    def test_str_nombre_apellido(self):
        """
        Comprueba que el valor por defecto __str__ devuelve el nombre más el apellido
        """
        member = Member.objects.get(name='Pepe')
        self.assertEqual(str(member), 'Pepe Perez')

    def test_charge_code(self):
        """
        Comprueba que el valor por defecto __str__ devuelve el nombre más el apellido
        """
        member = Member.objects.get(name='Pepe', sirname='Perez')
        self.assertEqual(member.charge_code, 'RG')