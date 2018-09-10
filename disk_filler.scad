thick = 2;
d_screw = 4;
r_screw = 78 / 2;
$fn = 100;

difference()
{
    cylinder(d = 90, h = thick, center = true);
    
    translate([0, r_screw, 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
    
    translate([r_screw, 0, 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
    
    translate([(r_screw)/sqrt(2), (r_screw)/sqrt(2), 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
    
    translate([0, -r_screw, 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
    
    translate([-r_screw, 0, 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
    
    translate([-(r_screw)/sqrt(2), -(r_screw)/sqrt(2), 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
        
    translate([-(r_screw)/sqrt(2), (r_screw)/sqrt(2), 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
    
    translate([(r_screw)/sqrt(2), -(r_screw)/sqrt(2), 0])
    #cylinder(d = d_screw, h = 2*thick, center = true);
}
