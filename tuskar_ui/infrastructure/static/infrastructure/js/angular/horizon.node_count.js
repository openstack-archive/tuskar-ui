angular.module('hz')
  .directive('hrNodeForm', ['hzConfig', function (hzConfig) {
    return {
      restrict: 'A',
      replace: false,
      transclude: true,
      scope: {},
      templateUrl: hzConfig.static_url + 'infrastructure/angular_templates/nodeform.html',
      controller: function ($scope) {
        var nodes = {};

        this.addRole = function (role, value) {
          nodes[role] = value;
          console.log(role);
          console.log(value);
        };
      }
    };
  }])
  .directive('hrNodeCount', ['hzConfig', function (hzConfig) {
    return {
      require: '^hrNodeForm',
      restrict: 'A',
      replace: true,
      transclude: true,
      scope: { initial_value: '=value' },
      templateUrl: hzConfig.static_url + 'infrastructure/angular_templates/numberpicker.html',
      link: function(scope, element, attrs, hrNodeForm) {
        input = element.find('input').first();
        angular.forEach(element[0].attributes, function(attribute) {
          input_attr = input.attr(attribute.nodeName);
          if (typeof input_attr === 'undefined' || input_attr === false) {
            input.attr(attribute.nodeName, attribute.nodeValue);
          }
        });

        scope.value = scope.initial_value;
        scope.disabledInput = (angular.isDefined(attrs.readonly)) ? true : false;

        hrNodeForm.addRole(input.attr('name'), scope.value);

        scope.disableArrow = function() {
          return (scope.value === 0) ? true : false;
        };

        scope.incrementValue = function() {
          if(!scope.disabledInput) {
            scope.value++;
          }
        };

        scope.decrementValue = function() {
          if(!scope.disabledInput && scope.value !== 0) {
            scope.value--;
          }
        };
      }
    };
  }]);
