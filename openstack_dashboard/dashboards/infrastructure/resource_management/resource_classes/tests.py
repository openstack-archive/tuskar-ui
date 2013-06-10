from collections import namedtuple

from django.core.urlresolvers import reverse

from openstack_dashboard.test import helpers as test


class ResourceClassViewTests(test.BaseAdminViewTests):

    def test_detail_get(self):
        ResourceClass = namedtuple('ResourceClass', 'id, name')
        resource_class = ResourceClass('1', 'test')

        url = reverse('horizon:infrastructure:resource_management:'
                      'resource_classes:detail', args=[resource_class.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(
            res, 'infrastructure/resource_management/resource_classes/'
                 'detail.html')

    # def test_detail_get_exception(self):
    #     index_url = reverse('horizon:infractructure:resource_management:'
    #                         'resource_classes:index')
    #     detail_url = reverse('horizon:infrastructure:resource_management:'
    #                          'resource_classes:detail', args=[42])

    #     res = self.client.get(detail_url)
    #     self.assertRedirectsNoFollow(res, index_url)
