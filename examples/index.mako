<!DOCTYPE html>
<html>
  <head>
  <title>Formbar Examples</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Bootstrap -->
  <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
  <link href="css/formbar.css" rel="stylesheet" media="screen">
  <link href="css/datepicker3.css" rel="stylesheet" media="screen">
  <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
  </style>
</head>
<body>
  <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    <div class="container">
      <div class="navbar-header">
        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
          <span class="sr-only">Toggle navigation</span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>
        <a class="navbar-brand" href="#">Formbar</a>
      </div>
      <div class="collapse navbar-collapse">
        <ul class="nav navbar-nav">
          <li class="active"><a href="example">Example</a></li>
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
  <div class="container">
  <h1>Formbar</h1>
  <p>Formbar is a python library form layouting, rendering and validating HTML
  forms in webapplications. The form renders a HTML form which can be used in
  connection with Twitter Bootstrap</p>
  <h2>Example 1</h2>
  ${form}
  </div> <!-- /container -->
  <script src="js/jquery.js"></script>
  <script src="bootstrap/js/bootstrap.min.js"></script>
  <script src="js/bootstrap-datepicker.js"></script>
  <script src="js/locales/bootstrap-datepicker.de.js"></script>
  <script src="js/formbar.js"></script>
  <script>
    $('#formbar-page-1').show();
  </script>
</body>
</html>
