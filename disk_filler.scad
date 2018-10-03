thick = 1.2;
d_screw = 4;
r_screw = (86.5 - d_screw) / 2;
$fn = 40;

difference()
{
    cylinder(d = 92, h = thick, center = true);
    
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
    
    cylinder(d = 10, h = 2*thick, center = true);
}
