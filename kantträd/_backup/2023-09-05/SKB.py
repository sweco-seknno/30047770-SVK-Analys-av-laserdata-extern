import os
import arcpy
arcpy.CheckOutExtension('3D')


def create_SKB_XYmZ(txt_file, gdb_name, fc_name, sr):

    fc_attributes = [['X', 'DOUBLE'],
                     ['Y', 'DOUBLE'],
                     ['Z', 'FLOAT'],
                     ['dZ', 'FLOAT'],
                     ['mZ', 'FLOAT']]

    fc_all_fields = ['X', 'Y', 'Z', 'dZ', 'mZ', 'SHAPE@XY', 'SHAPE@Z']

    txt_file_fields = ['X', 'Y', 'Z', 'dZ']

    arcpy.CreateFeatureclass_management(out_path=gdb_name, out_name=fc_name,
                                        geometry_type='POINT', has_z='ENABLED',
                                        spatial_reference=sr)

    for attribute in fc_attributes:
        arcpy.AddField_management(in_table=os.path.join(gdb_name, fc_name),
                                  field_name=attribute[0], field_type=attribute[1])

    # Read txt file, insert line by line in feature class
    with open(txt_file, 'r') as srcFile:
        fc = os.path.join(gdb_name, fc_name)
        with arcpy.da.InsertCursor(fc, fc_all_fields) as i_cursor:
            for fileLine in srcFile:
                lSplit = fileLine.split(' ')
                X = float(lSplit[0])
                Y = float(lSplit[1])
                Z = float(lSplit[2])
                dZ = float(lSplit[3])
                mZ = Z - dZ
                shapeXYZ = [(X, Y), mZ]
                row = [X, Y, Z, dZ, mZ] + shapeXYZ
                i_cursor.insertRow(row)


def create_SKB_XYZ(gdb, fc, fc_template, sr):
    # function to create fc_XYZ based on delivery template
    # only execute this if the fc does not already exist
    fc_full_path = os.path.join(gdb, fc)
    if arcpy.Exists(fc_full_path):
        print(fc+' already exists. Not created')
    else:
        arcpy.CreateFeatureclass_management(out_path=gdb, out_name=fc,
                                            geometry_type='POINT', template=fc_template,
                                            has_z='SAME_AS_TEMPLATE', spatial_reference=sr)


def dist_mZ_wire(gdb_name, fc_name, wires, radius):
    # Compute distance from tree ground point to wire
    # (Tree height can then be subtracted from this value to compute AVST_FAS)
    fc = os.path.join(gdb_name, fc_name)
    arcpy.Near3D_3d(in_features=fc, near_features=wires, search_radius=radius,
                    location="NO_LOCATION", angle="NO_ANGLE", delta="NO_DELTA")
    print('done with Near3D '+fc_name)
    arcpy.DeleteField_management(in_table=fc, drop_field='NEAR_FID')
    arcpy.AlterField_management(in_table=fc, field='NEAR_DIST',
                                new_field_name='AVSTAND_HORISONTELLT')
    arcpy.AlterField_management(in_table=fc, field='NEAR_DIST3',
                                new_field_name='AVST_MZ_FAS')
    print('done with deletefield '+fc_name)


def LG_name(LG):
    if LG <= 9:
        LG_str = 'LG00'+str(LG)
    elif LG <= 99:
        LG_str = 'LG0'+str(LG)
    else:
        LG_str = 'LG'+str(LG)

    return (LG_str)


def pick_out_akuta_and_traffpunkter(gdb, fc_in, fc_akuta, fc_trfpt, fc_intr_ers):
    # function for selecting
    # 1) akuta trad, and
    # 2) traffpunkter
    # and save in separate feature classes

    arcpy.Delete_management('trfpt_lyr')
    # Output to fc_akuta all trees in fc_in with AVSTAND_FAS <= 1
    fc_in_path = os.path.join(gdb, fc_in)
    arcpy.FeatureClassToFeatureClass_conversion(
        fc_in_path, gdb, fc_akuta, '"AVSTAND_FAS" <= 1', '#', '#')

    # Output to fc_trfpt all trees in fc_in with AVSTAND_FAS > 1
    arcpy.FeatureClassToFeatureClass_conversion(
        fc_in_path, gdb, fc_trfpt, '"AVSTAND_FAS" > 1', '#', '#')
    # Then select and delete trees from fc_trfpt that intersect intrangsersatt mark
    fc_trfpt_path = os.path.join(gdb, fc_trfpt)
    arcpy.MakeFeatureLayer_management(fc_trfpt_path, 'trfpt_lyr')
    arcpy.SelectLayerByLocation_management(
        'trfpt_lyr', 'INTERSECT', fc_intr_ers, '#', 'NEW_SELECTION')
    arcpy.DeleteFeatures_management('trfpt_lyr')
    arcpy.Delete_management('trfpt_lyr')


def pick_out_akuta(gdb, fc_in, fc_akuta):
    # Function for exporting akuta trad (avst_fas <= 1)
    fc_in_path = os.path.join(gdb, fc_in)
    # Export trees with avst_fas <= 1 to fc_akuta
    arcpy.FeatureClassToFeatureClass_conversion(
        fc_in_path, gdb, fc_akuta, '"AVSTAND_FAS" <= 1', '#', '#')


def pick_out_traffpunkter(gdb, fc_in, fc_trfpt, fc_intr_ers):
    # function for selection traffpunkter and save in separate feature class
    arcpy.Delete_management('trfpt_lyr')

    fc_in_path = os.path.join(gdb, fc_in)

    # Output to fc_trfpt all trees in fc_in with AVSTAND_FAS > 1
    arcpy.FeatureClassToFeatureClass_conversion(
        fc_in_path, gdb, fc_trfpt, '"AVSTAND_FAS" > 1', '#', '#')
    # Then select and delete trees from fc_trfpt that intersect intrangsersatt mark
    fc_trfpt_path = os.path.join(gdb, fc_trfpt)
    arcpy.MakeFeatureLayer_management(fc_trfpt_path, 'trfpt_lyr')
    arcpy.SelectLayerByLocation_management(
        'trfpt_lyr', 'INTERSECT', fc_intr_ers, '#', 'NEW_SELECTION')
    arcpy.DeleteFeatures_management('trfpt_lyr')
    arcpy.Delete_management('trfpt_lyr')


def pick_out_ej_akuta(gdb, fc_in, fc_ej_akuta):
    # function for selection traffpunkter and save in separate feature class
    fc_in_path = os.path.join(gdb, fc_in)
    # Export trees with avst_fas > 1 to fc_ej_akuta
    arcpy.FeatureClassToFeatureClass_conversion(
        fc_in_path, gdb, fc_ej_akuta, '"AVSTAND_FAS" > 1', '#', '#')


def populate_SKB_XYZ(input_fc, output_fc, LG, atgardsar, leverantor, ins_met, matosak_p, matosak_h):
    # reads the LG's fc_XYZmZ and writes to the LG'x fc_XYZ"

    LG_code_dict = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 70, 8: 80, 9: 90,
                    10: 100, 11: 110, 12: 120, 13: 130, 14: 140, 15: 150, 16: 160, 17: 170, 18: 180, 19: 190,
                    20: 200, 21: 210, 22: 220, 23: 230, 24: 240, 25: 250, 26: 260, 27: 270, 28: 280, 29: 290,
                    30: 300, 31: 310, 32: 320, 33: 330, 34: 340, 35: 350, 36: 360, 37: 370, 38: 380, 39: 390,
                    40: 400, 41: 410, 42: 420, 43: 430, 44: 440, 45: 450, 46: 460, 47: 470, 48: 480, 49: 490,
                    50: 500, 51: 510, 52: 520, 53: 530, 54: 540, 55: 550, 56: 560, 57: 570, 58: 580, 59: 590,
                    60: 600, 61: 610, 62: 620, 63: 630, 64: 640, 65: 650, 66: 660, 67: 670, 68: 680, 69: 690,
                    70: 700, 71: 710, 72: 720, 73: 730, 74: 740, 75: 750, 76: 760, 77: 770, 78: 780, 79: 790,
                    80: 800, 81: 810, 82: 820, 83: 830, 84: 840, 85: 850, 86: 860, 87: 870, 88: 880, 89: 890,
                    90: 900, 91: 910, 92: 920, 93: 930, 94: 940, 95: 950, 96: 951, 97: 952, 98: 953,
                    100: 960, 101: 970, 102: 980, 103: 990, 104: 1010, 105: 1020, 106: 1030, 107: 1040, 108: 1050, 109: 1060,
                    110: 1070, 111: 1080, 112: 1090, 113: 1100, 114: 1110, 115: 1120, 116: 1130, 117: 1140, 118: 1150, 119: 1160,
                    120: 1170, 121: 1180, 122: 1190, 123: 1200, 124: 1210, 125: 1220, 126: 1230, 127: 1240, 128: 1250, 129: 1260,
                    130: 1270, 131: 1280, 132: 1290, 133: 1300, 134: 1310, 135: 1320, 136: 1330, 137: 1340, 138: 1350, 139: 1360,
                    140: 1370, 141: 1380, 142: 1390, 143: 1400,
                    410: 1410, 500: 1420, 550: 1430, 555: 1435, 557: 1440, 661: 1450,
                    700: 1460, 701: 1470, 710: 1480, 720: 1490, 720: 1500, 730: 1510, 740: 1520, 750: 1530, 770: 1540}

    in_fields = ['SHAPE@XY', 'Z', 'dZ', 'AVSTAND_HORISONTELLT', 'AVST_MZ_FAS']

    out_fields = ['SHAPE@XY', 'SHAPE@Z', 'DELTA_HOJD', 'AVSTAND_FAS', 'MAX_TILLVAXT',
                  'AVSTAND_HORISONTELLT', 'LEDNINGSGATA', 'ATGARDSAR', 'LEVERANTOR',
                  'INSAMLINGSMETOD', 'MATOSAKERHET_PLAN', 'MATOSAKERHET_HOJD']

    LG_code = LG_code_dict[LG]

    with arcpy.da.SearchCursor(input_fc, in_fields) as s_cursor:
        with arcpy.da.InsertCursor(output_fc, out_fields) as i_cursor:
            for row in s_cursor:
                avst_fas = (row[4] - row[2])
                max_tillv = avst_fas - 1
                delta_hojd = row[2]
                avst_hori = row[3]
                z = row[1]  # - row[2]
                out_row = [row[0], z, delta_hojd, avst_fas, max_tillv, avst_hori, LG_code, atgardsar,
                           leverantor, ins_met, matosak_p, matosak_h]

                i_cursor.insertRow(out_row)


def remove_duplicates(gdb, fc_in, fc_out, xy_tol, z_tol):
    # Removes duplicates among akuta and traffpunkter, based on location.
    # Assumes that all instances in a "duplicate group" have identical
    # AVST_FAS etc (true if mZ was calculated for whole LG (all batches)
    # together, on all wires in the LG)
    input_fc = os.path.join(gdb, fc_in)
    no_dupl_fc = os.path.join(gdb, fc_out)

    arcpy.Copy_management(input_fc, no_dupl_fc)

    arcpy.DeleteIdentical_management(no_dupl_fc, ['Shape'], xy_tol, z_tol)


def compute_horizontal_dist(fc_in, wires, radius):
    # NEAR_DIST computed by Near3D, and then used as AvstHori in populate_SKB_XYZ,
    # does not seem to be the perpendicular distance to the wire, but rather the
    # distance to the nearest point on the wire (due to sag, I guess)
    # So: Use NEAR analysis in 2D to create a new NEAR column, then use that one as AvstHori
    arcpy.Near_analysis(in_features=fc_in, near_features=wires, search_radius=radius,
                        location="NO_LOCATION", angle="NO_ANGLE", method="PLANAR")


def update_z_coordinate(fd, fc):
    """New in 2023

    Updating z-coordinate from beeing treetop height to
    ground point z
    """

    arcpy.env.workspace = os.path.join(fd, fc)
    field = ['SHAPE@Z']
    cursor = arcpy.UpdateCursor(fc, field)

    s_field = ['DELTA_HOJD']
    s_cursor = arcpy.SearchCursor(fc, s_field)

    with arcpy.da.SearchCursor(fc, s_field) as s_cursor:
        with arcpy.da.UpdateCursor(fc, field) as cursor:
            for s_row, row in zip(s_cursor, cursor):
                row[0] = (row[0] - s_row[0])  # float(s_row[0])
                cursor.updateRow(row)

        # arcpy.AddField_management(fc,
        #                          "z", field_type="FLOAT")
        # geo = ['!Shape!.firstpoint.z']
        # arcpy.CalculateField_management(fc, "z", geo[0])


def update_horizontal_dist(fc_in):
    # put the horizontal distance calculated in compute_horizontal_dist
    # in the AvstHori field, and then remove the NEAR field
    near_field = 'NEAR_DIST'
    near_fid_field = 'NEAR_FID'
    avst_hori_field = 'AVSTAND_HORISONTELLT'
    update_fields = [avst_hori_field, near_field]

    with arcpy.da.UpdateCursor(fc_in, update_fields) as u_cursor:
        for row in u_cursor:
            row[0] = row[1]
            u_cursor.updateRow(row)

    arcpy.DeleteField_management(in_table=fc_in, drop_field=near_field)
    arcpy.DeleteField_management(in_table=fc_in, drop_field=near_fid_field)
