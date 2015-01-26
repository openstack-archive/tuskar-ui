(function() {
  'use strict';

  angular.module('tk.roles', [])
    .controller('tkRolesCtrl', function($scope, $http) {
      $scope.getRoles = function() {
        $http.get('/api/tuskar/roles/')
          .success(function(res) {
            $scope.roles = res.items;
          })
          .error(function(){
            // horizon.alert('error', gettext('Unable to retrieve roles'));
          });
      }

      $scope.getUsers();
  });

})();
