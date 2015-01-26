(function() {
  'use strict';

  angular.module('tk.roles', [])
    .controller('tkRolesCtrl', function($scope, $http) {

      // $scope.getRoles = function() {
      //   $http.get('/api/tuskar/roles/')
      //     .success(function(res) {
      //       $scope.roles = res.items;
      //     })
      //     .error(function(){
      //       horizon.alert('error', gettext('Unable to retrieve roles'));
      //     });
      // }

      // $scope.getRoles();

      $scope.roles = [
        {
            "description": "OpenStack swift storage node configured by Puppet",
            "name": "Swift-Storage",
            "uuid": "09b8ce5b-eaf5-48e1-929b-f622f3e89d89",
            "version": 1
        },
        {
            "description": "OpenStack ceph storage node configured by Puppet",
            "name": "Ceph-Storage",
            "uuid": "5f54622d-fd65-4c14-9d3c-ccf5d5d6e784",
            "version": 1
        },
        {
            "description": "OpenStack controller node configured by Puppet.\n",
            "name": "Controller",
            "uuid": "60e8d203-cb9e-48cb-9846-34b99f469cc0",
            "version": 1
        },
        {
            "description": "OpenStack cinder storage configured by Puppet",
            "name": "Cinder-Storage",
            "uuid": "915c549f-c9a4-41fa-ac8d-eae4dc339d68",
            "version": 1
        },
        {
            "description": "OpenStack hypervisor node configured via Puppet.\n",
            "name": "Compute",
            "uuid": "fcf7eadc-8313-4b83-9f11-f92d64e272f3",
            "version": 1
        }
    ];
  });

})();
