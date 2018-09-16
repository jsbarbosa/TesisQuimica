height = 47;
width = 34;
thick = 0.8;
z = 5;

difference()
{
    cube([height + 2*thick, width + 2*thick, z], center = true);
    translate([0, 0, thick / 2])
    #cube([height, width, z - thick], center = true);
}