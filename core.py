import math as m
import sys

# From local to world coordinates
def local_to_world(local, transform):
    return transform.transform(local)

# From world to local coordinates
def world_to_local(world, transform):
    inverse_transform = Matrix4()
    inverse_transform.set_inverse(transform)
    return inverse_transform.transform(world)

class Quaternion:
    def __init__(self, w=1, i=0, j=0, k=0):
        self.w = w
        self.i = i
        self.j = j
        self.k = k
    
    def __imul__(self, other):
        if isinstance(other, Quaternion):
            # Multiple quaternion with quaternion in place
            self.w = (self.w*other.w) - (self.i*other.i) - (self.j*other.j) - (self.k*other.k)
            self.i = (self.w*other.i) + (self.i*other.w) + (self.j*other.k) - (self.k*other.j)
            self.j = (self.w*other.j) + (self.j*other.w) + (self.k*other.i) - (self.i*other.k)
            self.k = (self.w*other.k) + (self.k*other.w) + (self.i*other.j) - (self.j*other.i)
            return self
        else:
            raise ValueError("Incompatible multiplication")
        
    def __mul__(self, other):
        if isinstance(other, Quaternion):
            # Multiple quaternion with quaternion
            quat = Quaternion(self.w, self.i, self.j, self.k)
            w = (quat.w*other.w) - (quat.i*other.i) - (quat.j*other.j) - (quat.k*other.k)
            i = (quat.w*other.i) + (quat.i*other.w) + (quat.j*other.k) - (quat.k*other.j)
            j = (quat.w*other.j) + (quat.j*other.w) + (quat.k*other.i) - (quat.i*other.k)
            k = (quat.w*other.k) + (quat.k*other.w) + (quat.i*other.j) - (quat.j*other.i)
            return Quaternion(w, i, j, k)
        
        elif isinstance(other, Vector3):
            # Convert the vector to a quaternion with 0 as the real part
            q_vec = Quaternion(0, other.x, other.y, other.z)
            # Perform the rotation: q^-1 * v * q (right-handed)
            q_inv = self.inverse()
            q_rotated = q_inv * q_vec * self
            # Return the rotated vector
            return Vector3(q_rotated.i, q_rotated.j, q_rotated.k)
        else:
            raise ValueError("Incompatible multiplication")

    # Adds the given vector to this, scaled by the given amount.
    # This is used to update the orientation quaternion by a rotation
    # and time.
    def add_scaled_vector(self, vec, scale):
        quat = Quaternion(0.0, vec.x*scale, vec.y*scale, vec.z*scale)
        this_self = Quaternion(self.w, self.i, self.j, self.k)
        quat *= this_self
        self.w += quat.w * (0.5)
        self.i += quat.i * (0.5)
        self.j += quat.j * (0.5)
        self.k += quat.k * (0.5)

    # Normalizes the quaternion to unit length, making it a valid
    # orientation quaternion
    def normalize(self):
        d = (self.w*self.w) + (self.i*self.i) + (self.j*self.j) + (self.k*self.k)

        # Check for zero length quaternion, and use the no-rotation
        # quaternion in that case
        if (d < sys.float_info.epsilon):
            self.w = 1
            self.i = 0
            self.j = 0
            self.k = 0
            return

        d = (1.0) / m.sqrt(d)
        self.w *= d
        self.i *= d
        self.j *= d
        self.k *= d

    # Rotate by vector
    def rotate_by_vector(self, vec):
        quat = Quaternion(0, vec.x, vec.y, vec.z)
        this_self = Quaternion(self.w, self.i, self.j, self.k)
        q = this_self * quat
        self.w = q.w
        self.i = q.i
        self.j = q.j
        self.k = q.k

class Matrix4:
    def __init__(self, a=1, b=0, c=0, d=0, e=0, f=1, g=0, h=0, i=0, j=0, k=1, l=0):
        # [a, b, c, d]  [0, 1, 2, 3]
        # [e, f, g, h]  [4, 5, 6, 7]
        # [i, j, k ,l]  [8, 9, 10, 11]
        # Holds the transform matrix data in array form
        self.data = [
            [a, b, c, d],  # First row
            [e, f, g, h],  # Second row
            [i, j, k, l]   # Third row
        ]

    def __mul__(self, other):
        if isinstance(other, Vector3):
            # Transform the given vector by this matrix
            x_ = self.data[0][0]*other.x + self.data[0][1]*other.y + self.data[0][2]*other.z + self.data[0][3]
            y_ = self.data[1][0]*other.x + self.data[1][1]*other.y + self.data[1][2]*other.z + self.data[1][3]
            z_ = self.data[2][0]*other.x + self.data[2][1]*other.y + self.data[2][2]*other.z + self.data[2][3]
            return Vector3(x_, y_, z_)
        elif isinstance(other, Matrix4):
            # Returns a matrix that is this matrix multiplied by the given other matrix
            result = Matrix4
            result.data[0][0] = (other.data[0][0]*self.data[0][0]) + (other.data[1][0]*self.data[0][1]) + (other.data[2][0]*self.data[0][2])
            result.data[1][0] = (other.data[0][0]*self.data[1][0]) + (other.data[1][0]*self.data[1][1]) + (other.data[2][0]*self.data[1][2])
            result.data[2][0] = (other.data[0][0]*self.data[2][0]) + (other.data[1][0]*self.data[2][1]) + (other.data[2][0]*self.data[2][2])

            result.data[0][1] = (other.data[0][1]*self.data[0][0]) + (other.data[1][1]*self.data[0][1]) + (other.data[2][1]*self.data[0][2])
            result.data[1][1] = (other.data[0][1]*self.data[1][0]) + (other.data[1][1]*self.data[1][1]) + (other.data[2][1]*self.data[1][2])
            result.data[2][1] = (other.data[0][1]*self.data[2][0]) + (other.data[1][1]*self.data[2][1]) + (other.data[2][1]*self.data[2][2])

            result.data[0][2] = (other.data[0][2]*self.data[0][0]) + (other.data[1][2]*self.data[0][1]) + (other.data[2][2]*self.data[0][2])
            result.data[1][2] = (other.data[0][2]*self.data[1][0]) + (other.data[1][2]*self.data[1][1]) + (other.data[2][2]*self.data[1][2])
            result.data[2][2] = (other.data[0][2]*self.data[2][0]) + (other.data[1][2]*self.data[2][1]) + (other.data[2][2]*self.data[2][2])

            result.data[0][3] = (other.data[0][3]*self.data[0][0]) + (other.data[1][3]*self.data[0][1]) + (other.data[2][3]*self.data[0][2]) + self.data[0][3]
            result.data[1][3] = (other.data[0][3]*self.data[1][0]) + (other.data[1][3]*self.data[1][1]) + (other.data[2][3]*self.data[1][2]) + self.data[1][3]
            result.data[2][3] = (other.data[0][3]*self.data[2][0]) + (other.data[1][3]*self.data[2][1]) + (other.data[2][3]*self.data[2][2]) + self.data[2][3]
            return result
        else:
            raise ValueError("Incompatible multiplication")

    # Gets a vector representing one axis in the matrix
    # The column to return
    def get_axis_vector(self, i):
        return Vector3(self.data[0][i], self.data[1][i], self.data[2][i])

    # Transform the given vector by the transformational inverse
    # of this matrix
    # NOTE: This function relies on the fact that the inverse of
    # a pure rotation matrix is its transpose. It separates the
    # translational and rotation components, transposes the
    # rotation, and multiplies out. If the matrix is not a
    # scale and shear free transform matrix, then this function
    # will not give correct results.
    def transform_inverse(self, vec):
        temp = vec
        temp.x -= self.data[0][3]
        temp.y -= self.data[1][3]
        temp.z -= self.data[2][3]
        x = (temp.x*self.data[0][0]) + (temp.y*self.data[1][0]) + (temp.z*self.data[2][0])
        y = (temp.x*self.data[0][1]) + (temp.y*self.data[1][1]) + (temp.z*self.data[2][1])
        z = (temp.x*self.data[0][2]) + (temp.y*self.data[1][2]) + (temp.z*self.data[2][2])
        return Vector3(x, y, z)
    
    # Transform the given direction vector by this matrix
    # NOTE: when a direction is converted between frames of 
    # reference, there is no translation required
    def transform_direction(self, vec):
        x = (vec.x*self.data[0][0]) + (vec.y*self.data[0][1]) + (vec.z*self.data[0][2])
        y = (vec.x*self.data[1][0]) + (vec.y*self.data[1][1]) + (vec.z*self.data[1][2])
        z = (vec.x*self.data[2][0]) + (vec.y*self.data[2][1]) + (vec.z*self.data[2][2])
        return Vector3(x, y, z)
    
    # Transform the given direction vector by the 
    # transformational inverse of this matrix
    # NOTE: This function relies on the fact that the inverse of
    # a pure rotation matrix is its transpose. It separates the
    # translational and rotation components, transposes the
    # rotation, and multiplies out. If the matrix is not a
    # scale and shear free transform matrix, then this function
    # will not give correct results.
    # NOTE: When a direction is converted between frames of
    # reference, there is no translation required.
    def transform_inverse_direction(self, vec):
        x = (vec.x*self.data[0][0]) + (vec.y*self.data[1][0]) + (vec.z*self.data[2][0])
        y = (vec.x*self.data[0][1]) + (vec.y*self.data[1][1]) + (vec.z*self.data[2][1])
        z = (vec.x*self.data[0][2]) + (vec.y*self.data[1][2]) + (vec.z*self.data[2][2])
        return Vector3(x, y, z)

    # Transform the given vector by this matrix
    def transform(self, vec):
        return self * vec

    # Sets the matrix to be a diagonal matrix with the given coefficients
    def set_diagonal(self, a, b, c):
        self.data[0][0] = a
        self.data[1][1] = b
        self.data[2][2] = c

    # Returns the determinant of the matrix
    def get_determinant(self, mat):
        x_1 = -mat.data[2][0]*mat.data[1][1]*mat.data[0][2]
        x_2 =  mat.data[1][0]*mat.data[2][1]*mat.data[0][2]
        x_3 =  mat.data[2][0]*mat.data[0][1]*mat.data[1][2]
        x_4 =  mat.data[0][0]*mat.data[2][1]*mat.data[1][2]
        x_5 =  mat.data[1][0]*mat.data[0][1]*mat.data[2][2]
        x_6 =  mat.data[0][0]*mat.data[1][1]*mat.data[2][2]
        return x_1 + x_2 + x_3 - x_4 - x_5 + x_6

    # Sets the matrix to be the inverse of the given matrix
    def set_inverse(self, mat):
        # Make sure the determinant is non-zero
        det = self.get_determinant(mat)
        if (det == 0):
            return
        det = 1.0/det

        self.data[0] = (-mat.data[2][1]*mat.data[1][2]+mat.data[1][1]*mat.data[2][2])*det
        self.data[4] = (mat.data[2][0]*mat.data[1][2]-mat.data[1][0]*mat.data[2][2])*det
        self.data[8] = (-mat.data[2][0]*mat.data[1][1]+mat.data[1][0]*mat.data[2][1])*det

        self.data[1] = (mat.data[2][1]*mat.data[0][2]-mat.data[0][1]*mat.data[2][2])*det
        self.data[5] = (-mat.data[2][0]*mat.data[0][2]+mat.data[0][0]*mat.data[2][2])*det
        self.data[9] = (mat.data[2][0]*mat.data[0][1]-mat.data[0][0]*mat.data[2][1])*det

        self.data[2] = (-mat.data[1][1]*mat.data[0][2]+mat.data[0][1]*mat.data[1][2])*det
        self.data[6] = (+mat.data[1][0]*mat.data[0][2]-mat.data[0][0]*mat.data[1][2])*det
        self.data[10] = (-mat.data[1][0]*mat.data[0][1]+mat.data[0][0]*mat.data[1][1])*det

        self.data[3] = (mat.data[2][1]*mat.data[1][2]*mat.data[0][3]
                -mat.data[1][1]*mat.data[2][2]*mat.data[0][3]
                -mat.data[2][1]*mat.data[0][2]*mat.data[1][3]
                +mat.data[0][1]*mat.data[2][2]*mat.data[1][3]
                +mat.data[1][1]*mat.data[0][2]*mat.data[2][3]
                -mat.data[0][1]*mat.data[1][2]*mat.data[2][3])*det
        self.data[7] = (-mat.data[2][0]*mat.data[1][2]*mat.data[0][3]
                +mat.data[1][0]*mat.data[2][2]*mat.data[0][3]
                +mat.data[2][0]*mat.data[0][2]*mat.data[1][3]
                -mat.data[0][0]*mat.data[2][2]*mat.data[1][3]
                -mat.data[1][0]*mat.data[0][2]*mat.data[2][3]
                +mat.data[0][0]*mat.data[1][2]*mat.data[2][3])*det
        self.data[11] =(mat.data[2][0]*mat.data[1][1]*mat.data[0][3]
                -mat.data[1][0]*mat.data[2][1]*mat.data[0][3]
                -mat.data[2][0]*mat.data[0][1]*mat.data[1][3]
                +mat.data[0][0]*mat.data[2][1]*mat.data[1][3]
                +mat.data[1][0]*mat.data[0][1]*mat.data[2][3]
                -mat.data[0][0]*mat.data[1][1]*mat.data[2][3])*det

    # Returns a new matrix containing the inverse of this matrix
    def inverse(self):
        result = Matrix4()
        result.set_inverse(self.data)
        return result

    # Inverts the matrix
    def invert(self):
        temp = self.data
        self.set_inverse(temp)

    # Sets this matrix to be the rotation matrix matrix corresponding to
    # the given quaternion
    def set_orientation_and_pos(self, quat, pos):
        self.data[0][0] = 1 - (2*quat.j*quat.j + 2*quat.k*quat.k)
        self.data[0][1] = 2*quat.i*quat.j + 2*quat.k*quat.w
        self.data[0][2] = 2*quat.i*quat.k - 2*quat.j*quat.w
        self.data[0][3] = pos.x

        self.data[1][0] = 2*quat.i*quat.j - 2*quat.k*quat.w
        self.data[1][1] = 1 - (2*quat.i*quat.i  + 2*quat.k*quat.k)
        self.data[1][2] = 2*quat.j*quat.k + 2*quat.i*quat.w
        self.data[1][3] = pos.y

        self.data[2][0] = 2*quat.i*quat.k + 2*quat.j*quat.w
        self.data[2][1] = 2*quat.j*quat.k - 2*quat.i*quat.w
        self.data[2][2] = 1 - (2*quat.i*quat.i  + 2*quat.j*quat.j)
        self.data[2][3] = pos.z

class Matrix3:
    def __init__(self, a=1, b=0, c=0, d=0, e=1, f=0, g=0, h=0, i=1):
        # [a, b, c]  [0, 1, 2]
        # [d, e, f]  [3, 4, 5]
        # [g, h, i]  [6, 7, 8]
        # Holds the tensor matrix data
        self.data = [
            [a, b, c],  # First row
            [d, e, f],  # Second row
            [g, h, i]   # Third row
        ]

    def __iadd__(self, other):
        if isinstance(other, Matrix3):
            # Does a component-wise addition of this matrix and the given matrix.
            self.data[0][0] += other.data[0][0]
            self.data[0][1] += other.data[0][1]
            self.data[0][2] += other.data[0][2]
            self.data[1][0] += other.data[1][0]
            self.data[1][1] += other.data[1][1]
            self.data[1][2] += other.data[1][2]
            self.data[2][0] += other.data[2][0]
            self.data[2][1] += other.data[2][1]
            self.data[2][2] += other.data[2][2]
        else:
            raise ValueError("Incompatible addition")

    def __imul__(self, other):
        if isinstance(other, Matrix3):
            # Multiplies this matrix in place by the given other matrix.
            self.data[0][0] = self.data[0][0]*other.data[0][0] + self.data[0][1]*other.data[1][0] + self.data[0][2]*other.data[2][0]
            self.data[0][1] = self.data[0][0]*other.data[0][1] + self.data[0][1]*other.data[1][1] + self.data[0][2]*other.data[2][1]
            self.data[0][2] = self.data[0][0]*other.data[0][2] + self.data[0][1]*other.data[1][2] + self.data[0][2]*other.data[2][2]

            self.data[1][0] = self.data[1][0]*other.data[0][0] + self.data[1][1]*other.data[1][0] + self.data[1][2]*other.data[2][0]
            self.data[1][1] = self.data[1][0]*other.data[0][1] + self.data[1][1]*other.data[1][1] + self.data[1][2]*other.data[2][1]
            self.data[1][2] = self.data[1][0]*other.data[0][2] + self.data[1][1]*other.data[1][2] + self.data[1][2]*other.data[2][2]

            self.data[2][0] = self.data[2][0]*other.data[0][0] + self.data[2][1]*other.data[1][0] + self.data[2][2]*other.data[2][0]
            self.data[2][1] = self.data[2][0]*other.data[0][1] + self.data[2][1]*other.data[1][1] + self.data[2][2]*other.data[2][1]
            self.data[2][2] = self.data[2][0]*other.data[0][2] + self.data[2][1]*other.data[1][2] + self.data[2][2]*other.data[2][2]

            return self
        
        elif isinstance(other, (int, float)):
            # Multiplies this matrix in place by the given scalar
            self.data[0][0] *= other
            self.data[0][1] *= other
            self.data[0][2] *= other
            self.data[1][0] *= other
            self.data[1][1] *= other
            self.data[1][2] *= other
            self.data[2][0] *= other
            self.data[2][1] *= other
            self.data[2][2] *= other
            return self

        else:
            raise ValueError("Incompatible multiplication")

    def __mul__(self, other):
        if isinstance(other, Vector3):
            # Transform the given vector by this matrix
            x_ = self.data[0][0]*other.x + self.data[0][1]*other.y + self.data[0][2]*other.z
            y_ = self.data[1][0]*other.x + self.data[1][1]*other.y + self.data[1][2]*other.z
            z_ = self.data[2][0]*other.x + self.data[2][1]*other.y + self.data[2][2]*other.z
            return Vector3(x_, y_, z_)
        elif isinstance(other, Matrix3):
            # Returns a matrix that is this matrix multiplied by the given other matrix
            result = Matrix3
            for i in range(3):
                for j in range(3):
                    result.data[i][j] = sum(self.data[i][k] * other.data[k][j] for k in range(3))
            return result
        else:
            raise ValueError("Incompatible multiplication")

    # Transform the given vector by this matrix
    def transform(self, vec):
        return self * vec
    
    # Transform the given vector by the transpose of this matrix
    def transform_transpose(self, vec):
        x = (vec.x * self.data[0][0]) + (vec.y * self.data[1][0]) + (vec.z * self.data[2][0])
        y = (vec.x * self.data[0][1]) + (vec.y * self.data[1][1]) + (vec.z * self.data[2][1])
        z = (vec.x * self.data[0][2]) + (vec.y * self.data[1][2]) + (vec.z * self.data[2][2])
        return Vector3(x, y, z)
    
    # Gets a vector representing one row in the matrix
    def get_row_vector(self, i):
        return Vector3(self.data[i][0], self.data[i][1], self.data[i][2])
    
    # Gets a vector representing one axis (column) in the matrix
    def get_axis_vector(self, i):
        return Vector3(self.data[0][i], self.data[1][i], self.data[2][i])

    # Sets the matrix to be the transpose of the given matrix
    def set_transpose(self, mat):
        self.data[0][0] = mat.data[0][0]
        self.data[0][1] = mat.data[1][0]
        self.data[0][2] = mat.data[2][0]
        self.data[1][0] = mat.data[0][1]
        self.data[1][1] = mat.data[1][1]
        self.data[1][2] = mat.data[2][1]
        self.data[2][0] = mat.data[0][2]
        self.data[2][1] = mat.data[1][2]
        self.data[2][2] = mat.data[2][2]

    # Returns a new matrix containing the transpose of this matrix
    def transpose(self):
        result = Matrix3()
        result.set_transpose(self.data)
        return result

    # Sets the matrix to be the inverse of the given matrix
    def set_inverse(self, mat):
        t4 = mat.data[0][0] * mat.data[1][1]
        t6 = mat.data[0][0] * mat.data[1][2]
        t8 = mat.data[0][1] * mat.data[1][0]
        t10 = mat.data[0][2] * mat.data[1][0]
        t12 = mat.data[0][1] * mat.data[2][0]
        t14 = mat.data[0][2] * mat.data[2][0]

        # Calculate the determinant
        t16 = (t4 * mat.data[2][2] - t6 * mat.data[2][1] - t8 * mat.data[2][2] +
               t10 * mat.data[2][1] + t12 * mat.data[1][2] - t14 * mat.data[1][1])

        # Make sure the determinant is non-zero.
        if t16 == 0.0:
            return  # The matrix is not invertible

        t17 = 1.0 / t16

        # Set the inverse matrix
        self.data[0][0] = (mat.data[1][1] * mat.data[2][2] - mat.data[1][2] * mat.data[2][1]) * t17
        self.data[0][1] = -(mat.data[0][1] * mat.data[2][2] - mat.data[0][2] * mat.data[2][1]) * t17
        self.data[0][2] = (mat.data[0][1] * mat.data[1][2] - mat.data[0][2] * mat.data[1][1]) * t17
        self.data[1][0] = -(mat.data[1][0] * mat.data[2][2] - mat.data[1][2] * mat.data[2][0]) * t17
        self.data[1][1] = (mat.data[0][0] * mat.data[2][2] - t14) * t17
        self.data[1][2] = -(t6 - t10) * t17
        self.data[2][0] = (mat.data[1][0] * mat.data[2][1] - mat.data[1][1] * mat.data[2][0]) * t17
        self.data[2][1] = -(mat.data[0][0] * mat.data[2][1] - t12) * t17
        self.data[2][2] = (t4 - t8) * t17
    
    # Returns a new matrix containing the inverse of this matrix
    def inverse(self):
        result = Matrix3
        result.set_inverse(self.data)
        return result
    
    # Inverts the matrix
    def invert(self):
        temp = self.data
        self.set_inverse(temp)

    # Sets the value of the matrix from inertia tensor values
    def set_inertia_tensor_coeffs(self, ix, iy, iz, ixy=0, ixz=0, iyz=0):
        self.data[0][0] = ix
        self.data[0][1] = -ixy
        self.data[0][2] = -ixz

        self.data[1][0] = -ixy
        self.data[1][1] = iy
        self.data[1][2] = -iyz

        self.data[2][0] = -ixz
        self.data[2][1] = -iyz
        self.data[2][2] = iz

    # Sets the matrix to be a diagonal matrix with the given
    # values along the leading diagonal
    def set_diagonal(self, a, b, c):
        self.set_inertia_tensor_coeffs(a, b, c)

    # Sets the value of the matrix as an inertia tensor of
    # a rectangular block aligned with the body's coordinate
    # system with the given axis half-size and mass
    def set_block_inertia_tensor(self, half_sizes, mass):
        sqaures = half_sizes.componentProduct(half_sizes)
        self.set_inertia_tensor_coeffs(0.3*mass(sqaures.y + sqaures.z),
                                    0.3*mass*(sqaures.x + sqaures.z),
                                    0.3*mass*(sqaures.x + sqaures.y))
        
    # Sets the matrix to be a skew symmetric matrix based on
    # the given vector. The skew symmetric matrix is the equivalent
    # of the vector product. So if a,b are vectors. axb = A_s b
    # where A_s is the skew symmetric form of a
    def set_skew_symmetric(self, vec):
        self.data[0][0] = self.data[1][1] = self.data[2][2] = 0
        self.data[0][1] = -vec.z
        self.data[0][2] = vec.y
        self.data[1][0] = vec.z
        self.data[1][2] = -vec.x
        self.data[2][0] = -vec.y
        self.data[2][1] = vec.x

    # Sets the matrix value from the given three vector components
    # These are arranged as the three columns of the vector
    def set_components(self, comp_one, comp_two, comp_three):
        self.data[0][0] = comp_one.x
        self.data[0][1] = comp_two.x
        self.data[0][2] = comp_three.x
        self.data[1][0] = comp_one.y
        self.data[1][1] = comp_two.y
        self.data[1][2] = comp_three.y
        self.data[2][0] = comp_one.z
        self.data[2][1] = comp_two.z
        self.data[2][2] = comp_three.z

    # Sets this matrix to be the rotation matrix corresponding to
    # the given quaternion
    def set_orientation(self, quat):
        self.data[0][0] = 1 - (2*quat.j*quat.j + 2*quat.k*quat.k)
        self.data[0][1] = 2*quat.i*quat.j + 2*quat.k*quat.w
        self.data[0][2] = 2*quat.i*quat.k - 2*quat.j*quat.w
        self.data[1][0] = 2*quat.i*quat.j - 2*quat.k*quat.w
        self.data[1][1] = 1 - (2*quat.i*quat.i  + 2*quat.k*quat.k)
        self.data[1][2] = 2*quat.j*quat.k + 2*quat.i*quat.w
        self.data[2][0] = 2*quat.i*quat.k + 2*quat.j*quat.w
        self.data[2][1] = 2*quat.j*quat.k - 2*quat.i*quat.w
        self.data[2][2] = 1 - (2*quat.i*quat.i  + 2*quat.j*quat.j)

    # Interpolates a couple of matrices
    def linear_interpolate(self, a, b, prop):
        result = Matrix3()
        for i in range(3):
            for j in range(3):
                result.data[i][j] = a.data[i][j] * (1 - prop) + b.data[i][j] * prop
        return result

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        # Holds the value along the x axis
        self.x = x
        # Holds the value along the y axis
        self.y = y
        # Holds the value along the z axis
        self.z = z

    def __add__(self, other):
        if isinstance(other, Vector3):
            # Adds the given vector to this
            x = self.x + other.x
            y = self.y + other.y
            z = self.z + other.z
            return Vector3(x, y, z)
        else:
            raise ValueError("Incompatible addition")

    def __iadd__(self, other):
        if isinstance(other, Vector3):
            # Adds the given vector to this
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self
        else:
            raise ValueError("Incompatible addition")

    def __sub__(self, other):
        if isinstance(other, Vector3):
            # Subtracts the given vector from this
            x = self.x - other.x
            y = self.y - other.y
            z = self.z - other.z
            return Vector3(x, y, z)
        else:
            raise ValueError("Incompatible subtraction")

    def __isub__(self, other):
        if isinstance(other, Vector3):
            # Subtracts the given vector from this
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            return self
        else:
            raise ValueError("Incompatible subtraction")

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            # Multiplies this vector by the given scalar
            self.x *= other
            self.y *= other
            self.z *= other
            return self
        else:
            raise ValueError("Incompatible multiplication")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            # Multiplies this vector by the given scalar
            self.x *= other
            self.y *= other
            self.z *= other
            return Vector3(self.x, self.y, self.z)
        elif isinstance(other, Vector3):
            # Calculates and returns the scalar product of this vector
            # with the given vector
            return self.x*other.x + self.y*other.y + self.z*other.z
        else:
            raise ValueError("Incompatible multiplication")

    def __rmul__(self, other):
        return self.__mul__(other)  # Allow other * Vector3 as well

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Vector3):
            return False
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def vectorProduct(self, vector):
        # Calculates and returns the vector product of this vector
        # with the given vector
        return Vector3(self.y*vector.z - self.z*vector.y,
                        self.z*vector.x - self.z*vector.z,
                        self.x*vector.y - self.z*vector.x)

    def componentProduct(self, vector):
        # Calculates the return of component-wise product of this
        # vector with the given vector
        return Vector3(self.x * vector.x, self.y * vector.y, self.z * vector.z)

    def componentProductUpdate(self, vector):
        # Perform a component-wise product with the given vector and
        # sets this vector to its result
        self.x *= vector.x
        self.y *= vector.y
        self.z *= vector.z

    def scalarProduct(self, vector):
        # Calculates and returns the scalar product of this vector
        # with the given vector
        return self.x*vector.x + self.y*vector.y + self.z*vector.z

    def invert(self):
        # Flip all the components of the vector
        self.x = -1*self.x
        self.y = -1*self.y
        self.z = -1*self.z

    def magnitude(self):
        # Gets the magnitude of this vector
        return m.sqrt(self.x**2 + self.y**2 + self.z**2 )

    def square_magnitude(self):
        # Gets the squared magnitude of this vector
        return self.x**2 + self.y**2 + self.z**2

    def trim(self, size):
        # Limits the size of the vector to the given maximum
        if (self.square_magnitude() > (size*size)):
            self.normalize()
            self.x *= size
            self.y *= size
            self.z *= size

    def normalize(self):
        # Turns a non-zero vector into a vector of unit length
        l = self.magnitude()
        if (l > 0):
            self.x *= 1.0 / l
            self.y *= 1.0 / l
            self.z *= 1.0 / l

    def addScaledVector(self, vector, scale):
        # Adds the given vector to this, scaled by the given amount
        self.x += vector.x * scale
        self.y += vector.y * scale
        self.z += vector.z * scale

    def clear(self):
        # Reset this vector in place
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def unit(self):
        # Returns the normalized version of a vector
        result = Vector3(self.x, self.y, self.z)
        result.normalize()
        return result

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_z(self, z):
        self.z = z