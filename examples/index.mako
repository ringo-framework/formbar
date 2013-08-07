<!DOCTYPE html>
<html>
  <head>
  <title>Formbar Examples</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Bootstrap -->
  <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
  <link href="bootstrap/css/formbar.css" rel="stylesheet" media="screen">
  <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
  </style>
</head>
<body>
  <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>
        <a class="brand" href="#">Formbar</a>
        <div class="nav-collapse collapse">
          <ul class="nav">
            <li class="active"><a href="example1">Example 1</a></li>
            <li class=""><a href="example2">Example 2</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
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
  <script src="bootstrap/js/jquery.js"></script>
  <script src="bootstrap/js/bootstrap.min.js"></script>
  <script src="bootstrap/js/bootstrap-datepicker.js"></script>
  <script src="bootstrap/js/formbar.js"></script>
</body>
</html>
